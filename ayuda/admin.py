from django.contrib import admin

from .models import PreguntaFrecuente


@admin.register(PreguntaFrecuente)
class PreguntaFrecuenteAdmin(admin.ModelAdmin):
    list_display = ['pregunta', 'categoria', 'orden', 'activa']
    list_filter = ['categoria', 'activa']
    search_fields = ['pregunta', 'respuesta']
    list_editable = ['orden', 'activa']
