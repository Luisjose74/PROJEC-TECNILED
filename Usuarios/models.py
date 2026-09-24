from django.contrib.auth.models import AbstractUser, Group
from django.db import models

# Permisos por defecto de cada rol. Se pueden ajustar luego en /admin/ -> Grupos.
PERMISOS_POR_ROL = {
    'administrador': ['gestionar_usuarios', 'gestionar_inventario', 'gestionar_compras'],
    'control_inventario': ['gestionar_inventario'],
    'cliente': [],
}


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMINISTRADOR = 'administrador', 'Administrador'
        CONTROL_INVENTARIO = 'control_inventario', 'Control de inventario'
        CLIENTE = 'cliente', 'Cliente'

    class EstadoCuenta(models.TextChoices):
        ACTIVA = 'activa', 'Activa'
        SUSPENDIDA = 'suspendida', 'Suspendida'
        BLOQUEADA = 'bloqueada', 'Bloqueada'

    email = models.EmailField('correo electrónico', unique=True)
    documento = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    estado_cuenta = models.CharField(
        max_length=12, choices=EstadoCuenta.choices, default=EstadoCuenta.ACTIVA
    )

    class Meta(AbstractUser.Meta):
        permissions = [
            ('gestionar_usuarios', 'Puede gestionar usuarios, roles y permisos'),
            ('gestionar_inventario', 'Puede gestionar el inventario'),
            ('gestionar_compras', 'Puede gestionar las compras a proveedores'),
        ]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        self.username = self.email
        self.is_active = self.estado_cuenta == self.EstadoCuenta.ACTIVA
        if self.is_superuser:
            self.rol = self.Rol.ADMINISTRADOR
        super().save(*args, **kwargs)
        self.sincronizar_grupo_por_rol()

    def sincronizar_grupo_por_rol(self):
        """Deja al usuario solo en el grupo que corresponde a su rol actual."""
        grupos_de_roles = Group.objects.filter(name__in=[r.label for r in self.Rol])
        self.groups.remove(*grupos_de_roles)
        grupo, _ = Group.objects.get_or_create(name=self.get_rol_display())
        self.groups.add(grupo)

    def __str__(self):
        return self.email