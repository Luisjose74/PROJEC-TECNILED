from django.conf import settings
from django.db import models
from django.utils import timezone


class RegistroRespaldo(models.Model):
    TIPOS = [('automatico', 'Automático'), ('manual', 'Manual')]
    ESTADOS = [('exitoso', 'Exitoso'), ('fallido', 'Fallido')]

    fecha = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    estado = models.CharField(max_length=10, choices=ESTADOS)
    ruta_archivo = models.CharField(max_length=500, blank=True)
    tamano = models.PositiveBigIntegerField(default=0, help_text='Bytes')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='respaldos',
    )
    detalle_error = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        permissions = [
            ('gestionar_respaldos', 'Puede generar, descargar y restaurar respaldos'),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} {self.fecha:%Y-%m-%d %H:%M} ({self.estado})'