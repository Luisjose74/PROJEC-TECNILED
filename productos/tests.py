import shutil
import tempfile
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from Usuarios.models import Usuario
from productos.models import Producto

# Las imágenes de los tests se guardan aquí y se borran al terminar
MEDIA_TEMPORAL = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)


def imagen_valida(nombre='foto.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, 'PNG')
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type='image/png')


def crear_usuario(correo, rol):
    return Usuario.objects.create_user(
        username=correo, email=correo, password='Prueba123!', rol=rol
    )


def crear_producto_bd(**overrides):
    datos = {
        'sku': 'E1', 'nombre': 'Cable THW Calibre 12',
        'categoria': Producto.Categoria.ELECTRICOS, 'precio': '45.00', 'stock': 50,
        'descripcion': 'Cable de cobre.', 'instalacion': 'Pelar los extremos.',
    }
    datos.update(overrides)
    return Producto.objects.create(**datos)


class ProductoModeloTests(TestCase):
    def test_precio_oferta_menor_al_precio_es_valido(self):
        p = Producto(
            sku='M1', nombre='X', precio='15.50', precio_oferta='12.00', stock=1,
            descripcion='d', instalacion='i',
        )
        p.full_clean()  # no debe lanzar excepción

    def test_precio_oferta_mayor_o_igual_al_precio_es_invalido(self):
        p = Producto(
            sku='M2', nombre='X', precio='10.00', precio_oferta='10.00', stock=1,
            descripcion='d', instalacion='i',
        )
        with self.assertRaises(ValidationError) as ctx:
            p.full_clean()
        self.assertIn('precio_oferta', ctx.exception.message_dict)

    def test_un_producto_nuevo_queda_activo_y_no_destacado(self):
        p = crear_producto_bd(sku='M3')
        self.assertTrue(p.activo)
        self.assertFalse(p.destacado_en_inicio)


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class RegistrarProductoTests(TestCase):
    """G1-141: Productos - Registrar producto."""

    def setUp(self):
        self.admin = crear_usuario('admin_prod@test.com', Usuario.Rol.ADMINISTRADOR)
        self.client.force_login(self.admin)

    def datos_validos(self, **overrides):
        datos = {
            'sku': 'E1', 'nombre': 'Cable THW Calibre 12',
            'categoria': Producto.Categoria.ELECTRICOS,
            'precio': '45.00', 'precio_oferta': '', 'stock': '50',
            'descripcion': 'Cable de cobre suave.', 'instalacion': 'Pelar los extremos.',
        }
        datos.update(overrides)
        return datos

    def test_registra_producto_y_redirige_al_listado(self):
        resp = self.client.post(reverse('crear_producto'), self.datos_validos())
        self.assertRedirects(resp, reverse('productos_lista'))
        p = Producto.objects.get(sku='E1')
        self.assertEqual(p.nombre, 'Cable THW Calibre 12')
        self.assertEqual(p.stock, 50)

    def test_producto_registrado_aparece_en_el_listado(self):
        self.client.post(reverse('crear_producto'), self.datos_validos())
        resp = self.client.get(reverse('productos_lista'))
        self.assertContains(resp, 'Cable THW Calibre 12')

    def test_control_inventario_tambien_puede_registrar(self):
        control = crear_usuario('inv_prod@test.com', Usuario.Rol.CONTROL_INVENTARIO)
        self.client.force_login(control)
        resp = self.client.post(reverse('crear_producto'), self.datos_validos())
        self.assertRedirects(resp, reverse('productos_lista'))

    def test_campos_obligatorios_vacios_no_crean_producto(self):
        resp = self.client.post(reverse('crear_producto'), {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Producto.objects.count(), 0)
        errores = resp.context['form'].errors
        for campo in ['sku', 'nombre', 'precio', 'stock', 'descripcion', 'instalacion']:
            self.assertIn(campo, errores)

    def test_sku_duplicado_no_crea_producto(self):
        crear_producto_bd(sku='E1')
        resp = self.client.post(
            reverse('crear_producto'), self.datos_validos(nombre='Otro nombre')
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Producto.objects.filter(sku='E1').count(), 1)

    def test_precio_oferta_mayor_al_precio_es_rechazado(self):
        resp = self.client.post(
            reverse('crear_producto'), self.datos_validos(precio_oferta='50.00')
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Producto.objects.filter(sku='E1').exists())
        self.assertContains(resp, 'El precio de oferta debe ser menor al precio normal.')

    def test_categoria_invalida_manipulada_es_rechazada(self):
        resp = self.client.post(
            reverse('crear_producto'), self.datos_validos(categoria='hacker')
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Producto.objects.filter(sku='E1').exists())

    def test_stock_negativo_es_rechazado(self):
        resp = self.client.post(reverse('crear_producto'), self.datos_validos(stock='-5'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Producto.objects.filter(sku='E1').exists())

    def test_cliente_recibe_403(self):
        cliente = crear_usuario('cliente_prod@test.com', Usuario.Rol.CLIENTE)
        self.client.force_login(cliente)
        resp = self.client.get(reverse('crear_producto'))
        self.assertEqual(resp.status_code, 403)

    def test_usuario_sin_sesion_no_accede(self):
        self.client.logout()
        resp = self.client.get(reverse('crear_producto'))
        self.assertEqual(resp.status_code, 302)


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class CargarImagenTests(TestCase):
    """G1-142: Productos - Cargar imagen."""

    def setUp(self):
        self.admin = crear_usuario('admin_img@test.com', Usuario.Rol.ADMINISTRADOR)
        self.client.force_login(self.admin)

    def datos(self, **overrides):
        datos = {
            'sku': 'I1', 'nombre': 'Lámpara Colgante Moderna',
            'categoria': Producto.Categoria.INTERIORES,
            'precio': '65.00', 'precio_oferta': '', 'stock': '8',
            'descripcion': 'Lámpara.', 'instalacion': 'Colgar del techo.',
        }
        datos.update(overrides)
        return datos

    def test_imagen_valida_se_almacena(self):
        resp = self.client.post(
            reverse('crear_producto'), self.datos(imagen=imagen_valida())
        )
        self.assertRedirects(resp, reverse('productos_lista'))
        p = Producto.objects.get(sku='I1')
        self.assertTrue(p.imagen)
        self.assertTrue(p.imagen.name.startswith('productos/'))
        self.assertTrue(p.imagen.storage.exists(p.imagen.name))

    def test_imagen_guardada_se_muestra_en_el_listado(self):
        self.client.post(reverse('crear_producto'), self.datos(imagen=imagen_valida()))
        resp = self.client.get(reverse('productos_lista'))
        self.assertContains(resp, 'media/productos/')

    def test_archivo_que_no_es_imagen_es_rechazado(self):
        falso = SimpleUploadedFile('virus.png', b'esto no es una imagen', content_type='image/png')
        resp = self.client.post(reverse('crear_producto'), self.datos(imagen=falso))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Producto.objects.filter(sku='I1').exists())

    def test_se_puede_registrar_sin_imagen(self):
        resp = self.client.post(reverse('crear_producto'), self.datos())
        self.assertRedirects(resp, reverse('productos_lista'))
        self.assertFalse(Producto.objects.get(sku='I1').imagen)


class BuscarProductosTests(TestCase):
    """G1-143: Productos - Buscar productos."""

    def setUp(self):
        self.admin = crear_usuario('admin_lista_prod@test.com', Usuario.Rol.ADMINISTRADOR)
        crear_producto_bd(sku='E1', nombre='Cable THW Calibre 12')
        crear_producto_bd(
            sku='I1', nombre='Lámpara Colgante Moderna',
            categoria=Producto.Categoria.INTERIORES,
        )
        self.client.force_login(self.admin)

    def test_busqueda_encuentra_por_nombre(self):
        resp = self.client.get(reverse('productos_lista'), {'q': 'Cable'})
        self.assertContains(resp, 'Cable THW Calibre 12')
        self.assertNotContains(resp, 'Lámpara Colgante Moderna')

    def test_busqueda_no_distingue_mayusculas(self):
        resp = self.client.get(reverse('productos_lista'), {'q': 'cable thw'})
        self.assertContains(resp, 'Cable THW Calibre 12')

    def test_busqueda_encuentra_por_codigo(self):
        resp = self.client.get(reverse('productos_lista'), {'q': 'I1'})
        self.assertContains(resp, 'Lámpara Colgante Moderna')
        self.assertNotContains(resp, 'Cable THW Calibre 12')

    def test_busqueda_sin_resultados_muestra_mensaje(self):
        resp = self.client.get(reverse('productos_lista'), {'q': 'noexiste'})
        self.assertContains(resp, 'No se encontraron productos.')

    def test_sin_busqueda_muestra_todos(self):
        resp = self.client.get(reverse('productos_lista'))
        self.assertContains(resp, 'Cable THW Calibre 12')
        self.assertContains(resp, 'Lámpara Colgante Moderna')

    def test_filtro_por_categoria(self):
        resp = self.client.get(reverse('productos_lista'), {'categoria': 'interiores'})
        self.assertContains(resp, 'Lámpara Colgante Moderna')
        self.assertNotContains(resp, 'Cable THW Calibre 12')

    def test_categoria_invalida_en_la_url_se_ignora(self):
        resp = self.client.get(reverse('productos_lista'), {'categoria': 'hacker'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Cable THW Calibre 12')

    def test_busqueda_y_categoria_se_combinan(self):
        resp = self.client.get(
            reverse('productos_lista'), {'q': 'Cable', 'categoria': 'interiores'}
        )
        self.assertContains(resp, 'No se encontraron productos.')

    def test_paginacion_limita_a_10_por_pagina(self):
        for i in range(15):
            crear_producto_bd(sku=f'P{i}', nombre=f'Producto de prueba {i}')
        resp = self.client.get(reverse('productos_lista'))
        self.assertEqual(len(resp.context['productos']), 10)

    def test_segunda_pagina_conserva_la_busqueda(self):
        for i in range(15):
            crear_producto_bd(sku=f'P{i}', nombre=f'Producto de prueba {i}')
        resp = self.client.get(reverse('productos_lista'), {'q': 'Producto de prueba', 'page': 2})
        self.assertEqual(len(resp.context['productos']), 5)
        self.assertEqual(resp.context['query'], 'Producto de prueba')

    def test_cliente_recibe_403(self):
        cliente = crear_usuario('cliente_lista_prod@test.com', Usuario.Rol.CLIENTE)
        self.client.force_login(cliente)
        resp = self.client.get(reverse('productos_lista'))
        self.assertEqual(resp.status_code, 403)
        
        
class DestacarEnInicioTests(TestCase):
    """Interruptor 'Destacado en Inicio' (G1-148)."""

    def setUp(self):
        self.admin = crear_usuario('admin_dest@test.com', Usuario.Rol.ADMINISTRADOR)
        self.producto = crear_producto_bd(sku='D1', nombre='Producto destacable')
        self.client.force_login(self.admin)

    def test_alterna_a_destacado_y_de_vuelta(self):
        url = reverse('alternar_destacado', args=[self.producto.pk])
        self.client.post(url)
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.destacado_en_inicio)
        self.client.post(url)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.destacado_en_inicio)

    def test_vuelve_a_la_pagina_con_la_busqueda(self):
        url = reverse('alternar_destacado', args=[self.producto.pk])
        resp = self.client.post(url, {'next': '/productos/?q=destacable'})
        self.assertRedirects(resp, '/productos/?q=destacable')

    def test_next_hacia_otro_sitio_es_ignorado(self):
        url = reverse('alternar_destacado', args=[self.producto.pk])
        resp = self.client.post(url, {'next': 'https://sitio-malicioso.com'})
        self.assertRedirects(resp, reverse('productos_lista'))

    def test_get_no_esta_permitido(self):
        resp = self.client.get(reverse('alternar_destacado', args=[self.producto.pk]))
        self.assertEqual(resp.status_code, 405)

    def test_cliente_recibe_403_y_no_cambia_nada(self):
        cliente = crear_usuario('cliente_dest@test.com', Usuario.Rol.CLIENTE)
        self.client.force_login(cliente)
        resp = self.client.post(reverse('alternar_destacado', args=[self.producto.pk]))
        self.assertEqual(resp.status_code, 403)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.destacado_en_inicio)