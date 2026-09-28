from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'first_name', 'last_name', 'rol', 'estado_cuenta', 'is_staff')
    list_filter = ('rol', 'estado_cuenta', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'documento')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'documento', 'telefono')}),
        ('Rol y estado', {'fields': ('rol', 'estado_cuenta')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'rol', 'password1', 'password2'),
        }),
    )

# Register your models here.
