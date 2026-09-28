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