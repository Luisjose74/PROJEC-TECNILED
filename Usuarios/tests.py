from django.test import TestCase

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