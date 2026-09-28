from django.apps import AppConfig
from django.db.models.signals import post_migrate


def crear_grupos_por_rol(sender, **kwargs):
    from django.contrib.auth.management import create_permissions
    from django.contrib.auth.models import Group, Permission

    from .models import PERMISOS_POR_ROL, Usuario

    create_permissions(sender, verbosity=0)
    for valor, codenames in PERMISOS_POR_ROL.items():
        grupo, creado = Group.objects.get_or_create(name=Usuario.Rol(valor).label)
        if creado:  # no pisamos cambios hechos luego desde /admin/
            grupo.permissions.set(
                Permission.objects.filter(
                    content_type__app_label='Usuarios',
                    content_type__model='usuario',
                    codename__in=codenames,
                )
            )


class UsuariosConfig(AppConfig):
    name = 'Usuarios'

    def ready(self):
        post_migrate.connect(crear_grupos_por_rol, sender=self)