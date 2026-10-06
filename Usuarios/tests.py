from datetime import timedelta
from django.test import override_settings
from django.utils import timezone
from Usuarios.models import CodigoRecuperacion
from django.test import TestCase
from django.urls import reverse
from Usuarios.models import Usuario


class RolesYPermisosTests(TestCase):
    def crear(self, correo, rol):
        return Usuario.objects.create_user(
            username=correo, email=correo, password='Prueba123!', rol=rol
        )

    def recargar(self, usuario):
        # has_perm guarda una caché por instancia: volvemos a leer de la BD
        return Usuario.objects.get(pk=usuario.pk)

    def test_cliente_no_tiene_permisos_de_gestion(self):
        u = self.crear('cliente@test.com', Usuario.Rol.CLIENTE)
        self.assertFalse(u.has_perm('Usuarios.gestionar_usuarios'))
        self.assertFalse(u.has_perm('Usuarios.gestionar_inventario'))
        self.assertFalse(u.has_perm('Usuarios.gestionar_compras'))

    def test_control_inventario_solo_gestiona_inventario(self):
        u = self.crear('inv@test.com', Usuario.Rol.CONTROL_INVENTARIO)
        self.assertTrue(u.has_perm('Usuarios.gestionar_inventario'))
        self.assertFalse(u.has_perm('Usuarios.gestionar_usuarios'))

    def test_administrador_tiene_todos_los_permisos(self):
        u = self.crear('admin@test.com', Usuario.Rol.ADMINISTRADOR)
        self.assertTrue(u.has_perm('Usuarios.gestionar_usuarios'))
        self.assertTrue(u.has_perm('Usuarios.gestionar_inventario'))
        self.assertTrue(u.has_perm('Usuarios.gestionar_compras'))

    def test_cambiar_rol_actualiza_los_permisos(self):
        u = self.crear('cambio@test.com', Usuario.Rol.CLIENTE)
        u.rol = Usuario.Rol.CONTROL_INVENTARIO
        u.save()
        self.assertTrue(self.recargar(u).has_perm('Usuarios.gestionar_inventario'))
        u.rol = Usuario.Rol.CLIENTE
        u.save()
        self.assertFalse(self.recargar(u).has_perm('Usuarios.gestionar_inventario'))
        self.assertEqual(u.groups.count(), 1)


class UsuariosListaTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username='admin_lista@test.com', email='admin_lista@test.com',
            password='Prueba123!', rol=Usuario.Rol.ADMINISTRADOR,
        )
        Usuario.objects.create_user(
            username='ana@test.com', email='ana@test.com', password='Prueba123!',
            first_name='Ana', last_name='Perez', documento='111', rol=Usuario.Rol.CLIENTE,
        )
        Usuario.objects.create_user(
            username='luis@test.com', email='luis@test.com', password='Prueba123!',
            first_name='Luis', last_name='Gomez', documento='222', rol=Usuario.Rol.CLIENTE,
        )

    def test_requiere_permiso_gestionar_usuarios(self):
        cliente = Usuario.objects.create_user(
            username='sinpermiso@test.com', email='sinpermiso@test.com',
            password='Prueba123!', rol=Usuario.Rol.CLIENTE,
        )
        self.client.force_login(cliente)
        resp = self.client.get(reverse('usuarios_lista'))
        self.assertEqual(resp.status_code, 403)

    def test_busqueda_encuentra_por_nombre(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('usuarios_lista'), {'q': 'Ana'})
        self.assertContains(resp, 'ana@test.com')
        self.assertNotContains(resp, 'luis@test.com')

    def test_busqueda_sin_resultados_muestra_mensaje(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('usuarios_lista'), {'q': 'noexiste'})
        self.assertContains(resp, 'No se encontraron usuarios.')

    def test_paginacion_limita_a_10_por_pagina(self):
        for i in range(15):
            Usuario.objects.create_user(
                username=f'user{i}@test.com', email=f'user{i}@test.com',
                password='Prueba123!', rol=Usuario.Rol.CLIENTE,
            )
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('usuarios_lista'))
        self.assertEqual(len(resp.context['usuarios']), 10)


class CrearUsuarioInternoTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username='admin_crear@test.com', email='admin_crear@test.com',
            password='Prueba123!', rol=Usuario.Rol.ADMINISTRADOR,
        )
        self.client.force_login(self.admin)

    def datos_validos(self, **overrides):
        datos = {
            'first_name': 'Nueva', 'apellido': 'Cuenta', 'email': 'nueva@test.com',
            'documento': '999', 'telefono': '3000000000',
            'rol': Usuario.Rol.CONTROL_INVENTARIO, 'contrasena': 'Segura123!',
        }
        datos.update(overrides)
        return datos

    def test_crea_cuenta_con_rol_asignado(self):
        resp = self.client.post(reverse('crear_usuario'), self.datos_validos())
        self.assertRedirects(resp, reverse('usuarios_lista'))
        creado = Usuario.objects.get(email='nueva@test.com')
        self.assertEqual(creado.rol, Usuario.Rol.CONTROL_INVENTARIO)
        self.assertTrue(creado.check_password('Segura123!'))

    def test_correo_duplicado_no_crea_cuenta(self):
        Usuario.objects.create_user(username='dup@test.com', email='dup@test.com', password='Prueba123!')
        resp = self.client.post(reverse('crear_usuario'), self.datos_validos(email='dup@test.com'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Usuario.objects.filter(email='dup@test.com').count(), 1)

    def test_documento_duplicado_no_crea_cuenta(self):
        Usuario.objects.create_user(username='otro@test.com', email='otro@test.com',
                                     password='Prueba123!', documento='999')
        resp = self.client.post(reverse('crear_usuario'), self.datos_validos(email='nueva2@test.com'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Usuario.objects.filter(email='nueva2@test.com').exists())

    def test_rol_invalido_manipulado_es_rechazado(self):
        resp = self.client.post(reverse('crear_usuario'), self.datos_validos(rol='hacker'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Usuario.objects.filter(email='nueva@test.com').exists())

    def test_requiere_permiso_gestionar_usuarios(self):
        cliente = Usuario.objects.create_user(
            username='sinpermiso2@test.com', email='sinpermiso2@test.com',
            password='Prueba123!', rol=Usuario.Rol.CLIENTE,
        )
        self.client.force_login(cliente)
        resp = self.client.get(reverse('crear_usuario'))
        self.assertEqual(resp.status_code, 403)


class EditarRolTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username='admin_rol@test.com', email='admin_rol@test.com',
            password='Prueba123!', rol=Usuario.Rol.ADMINISTRADOR,
        )
        self.usuario = Usuario.objects.create_user(
            username='cambia@test.com', email='cambia@test.com',
            password='Prueba123!', rol=Usuario.Rol.CLIENTE,
        )

    def test_admin_cambia_rol_y_actualiza_permisos(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('editar_rol', args=[self.usuario.pk]),
            {'rol': Usuario.Rol.CONTROL_INVENTARIO, 'estado_cuenta': Usuario.EstadoCuenta.ACTIVA},
        )
        self.assertRedirects(resp, reverse('usuarios_lista'))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.rol, Usuario.Rol.CONTROL_INVENTARIO)
        self.assertTrue(self.usuario.has_perm('Usuarios.gestionar_inventario'))

    def test_admin_no_puede_quitarse_su_propio_rol(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse('editar_rol', args=[self.admin.pk]),
            {'rol': Usuario.Rol.CLIENTE, 'estado_cuenta': Usuario.EstadoCuenta.ACTIVA},
        )
        self.assertEqual(resp.status_code, 200)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.rol, Usuario.Rol.ADMINISTRADOR)

    def test_usuario_sin_permiso_no_puede_modificar_rol_de_otro(self):
        self.client.force_login(self.usuario)
        otro = Usuario.objects.create_user(
            username='otro2@test.com', email='otro2@test.com',
            password='Prueba123!', rol=Usuario.Rol.CLIENTE,
        )
        resp = self.client.get(reverse('editar_rol', args=[otro.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_funcionalidades_disponibles_cambian_segun_permiso(self):
        control = Usuario.objects.create_user(
            username='inv2@test.com', email='inv2@test.com',
            password='Prueba123!', rol=Usuario.Rol.CONTROL_INVENTARIO,
        )
        self.client.force_login(control)
        resp = self.client.get(reverse('usuarios_lista'))
        self.assertEqual(resp.status_code, 403)
        
class PlantillasBaseTests(TestCase):
    """G1-1190: las pantallas de administración usan admin_base.html."""

    def setUp(self):
        # Antes de cada prueba: crear un administrador e iniciar sesión
        self.admin = Usuario.objects.create_user(
            username='luis.silva@tecniled.com', email='luis.silva@tecniled.com',
            password='Prueba123!', first_name='Luis José', last_name='Silva Fajardo',
            rol=Usuario.Rol.ADMINISTRADOR,
        )
        self.client.force_login(self.admin)

    def test_usuarios_lista_usa_admin_base(self):
        # 1) Abrir la página /usuarios/
        resp = self.client.get(reverse('usuarios_lista'))
        # 2) Debe usar la plantilla del panel...
        self.assertTemplateUsed(resp, 'admin_base.html')
        # 3) ...y NO la plantilla de la tienda
        self.assertTemplateNotUsed(resp, 'base.html')

    def test_usuarios_lista_muestra_titulo_y_miga(self):
        # 1) Abrir la página /usuarios/
        resp = self.client.get(reverse('usuarios_lista'))
        # 2) El título y la miga deben decir "Gestión de usuarios" (con tilde)
        self.assertContains(resp, 'Gestión de usuarios')
        
    def test_usuarios_crear_usa_admin_base(self):
        resp = self.client.get(reverse('crear_usuario'))
        self.assertTemplateUsed(resp, 'admin_base.html')
        self.assertTemplateNotUsed(resp, 'base.html')
        self.assertContains(resp, 'Nuevo administrador')
        
class BloqueoCuentaTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='bloq@test.com', email='bloq@test.com',
            password='Prueba123!', rol=Usuario.Rol.CLIENTE,
        )

    def intentar(self, clave):
        return self.client.post(reverse('login'), {'correo': 'bloq@test.com', 'contrasena': clave})

    def test_tres_fallos_bloquean_la_cuenta(self):
        for _ in range(3):
            self.intentar('mala')
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.estado_cuenta, Usuario.EstadoCuenta.BLOQUEADA)
        self.assertFalse(self.usuario.is_active)

    def test_dos_fallos_no_bloquean(self):
        self.intentar('mala')
        self.intentar('mala')
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.estado_cuenta, Usuario.EstadoCuenta.ACTIVA)

    def test_cuenta_bloqueada_no_entra_ni_con_clave_correcta(self):
        for _ in range(3):
            self.intentar('mala')
        resp = self.intentar('Prueba123!')
        self.assertContains(resp, 'bloqueada')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_exitoso_reinicia_el_contador(self):
        self.intentar('mala')
        self.intentar('mala')
        self.intentar('Prueba123!')
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.intentos_fallidos, 0)

    def test_admin_reactiva_y_el_contador_vuelve_a_cero(self):
        for _ in range(3):
            self.intentar('mala')
        self.usuario.refresh_from_db()
        self.usuario.estado_cuenta = Usuario.EstadoCuenta.ACTIVA
        self.usuario.save()
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.intentos_fallidos, 0)
        self.assertTrue(self.usuario.is_active)
        
# MD5 solo en pruebas: hace los tests mucho más rápidos. En producción se usa el hasher normal.
@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CodigoRecuperacionTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='rec@test.com', email='rec@test.com',
            password='Prueba123!', rol=Usuario.Rol.CLIENTE,
        )

    def test_genera_codigo_de_6_digitos_y_no_lo_guarda_en_claro(self):
        objeto, codigo = CodigoRecuperacion.generar(self.usuario)
        self.assertEqual(len(codigo), 6)
        self.assertTrue(codigo.isdigit())
        self.assertNotEqual(objeto.codigo_hash, codigo)

    def test_codigo_correcto_es_valido(self):
        objeto, codigo = CodigoRecuperacion.generar(self.usuario)
        self.assertTrue(objeto.validar(codigo))

    def test_codigo_incorrecto_es_rechazado_y_cuenta_el_intento(self):
        objeto, codigo = CodigoRecuperacion.generar(self.usuario)
        incorrecto = '000000' if codigo != '000000' else '111111'
        self.assertFalse(objeto.validar(incorrecto))
        objeto.refresh_from_db()
        self.assertEqual(objeto.intentos, 1)

    def test_codigo_vencido_es_rechazado(self):
        objeto, codigo = CodigoRecuperacion.generar(self.usuario)
        objeto.expira_en = timezone.now() - timedelta(minutes=1)
        objeto.save()
        self.assertFalse(objeto.validar(codigo))

    def test_codigo_usado_no_se_puede_reutilizar(self):
        objeto, codigo = CodigoRecuperacion.generar(self.usuario)
        self.assertTrue(objeto.validar(codigo))
        objeto.marcar_usado()
        self.assertFalse(objeto.validar(codigo))

    def test_codigo_nuevo_invalida_el_anterior(self):
        primero, codigo1 = CodigoRecuperacion.generar(self.usuario)
        segundo, codigo2 = CodigoRecuperacion.generar(self.usuario)
        primero.refresh_from_db()
        self.assertFalse(primero.validar(codigo1))
        self.assertTrue(segundo.validar(codigo2))

    def test_tras_5_intentos_fallidos_el_codigo_queda_inutilizable(self):
        objeto, codigo = CodigoRecuperacion.generar(self.usuario)
        incorrecto = '000000' if codigo != '000000' else '111111'
        for _ in range(CodigoRecuperacion.MAX_INTENTOS):
            objeto.validar(incorrecto)
        self.assertFalse(objeto.validar(codigo))  # ni con el código correcto

    def test_ultimo_vigente_devuelve_none_si_no_hay(self):
        self.assertIsNone(CodigoRecuperacion.ultimo_vigente(self.usuario))
        objeto, _ = CodigoRecuperacion.generar(self.usuario)
        self.assertEqual(CodigoRecuperacion.ultimo_vigente(self.usuario), objeto)
