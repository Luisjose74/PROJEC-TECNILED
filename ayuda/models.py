from django.db import models


class PreguntaFrecuente(models.Model):
    """Una pregunta del módulo de ayuda. El administrador las gestiona desde /admin/."""

    class Categoria(models.TextChoices):
        GENERAL = 'general', 'General'
        CUENTA = 'cuenta', 'Mi cuenta'
        COMPRAS = 'compras', 'Compras y pedidos'
        INVENTARIO = 'inventario', 'Productos e inventario'
        ADMINISTRACION = 'administracion', 'Administración'

    pregunta = models.CharField(max_length=200)
    respuesta = models.TextField()
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.GENERAL)
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['categoria', 'orden']
        verbose_name = 'pregunta frecuente'
        verbose_name_plural = 'preguntas frecuentes'

    def __str__(self):
        return self.pregunta
