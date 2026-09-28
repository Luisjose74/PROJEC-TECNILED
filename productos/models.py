from django.core.exceptions import ValidationError
from django.db import models


class Producto(models.Model):
    class Categoria(models.TextChoices):
        # Mismos 4 valores que el <select name="category"> del diseño (AdminDashboard.tsx)
        ELECTRICOS = 'electricos', 'Eléctricos'
        INTERIORES = 'interiores', 'Interiores'
        FERRETERIA = 'ferreteria', 'Ferretería'
        ILUMINACION = 'iluminacion', 'Iluminación'

    # --- Identificación ---
    sku = models.CharField(
        'Código (SKU)', max_length=30, unique=True,
        help_text='Código único del producto. Se usa para buscarlo rápidamente.',
    )
    nombre = models.CharField('Título', max_length=150)

    # --- Clasificación y precio (campos del formulario del diseño) ---
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.ELECTRICOS)
    precio = models.DecimalField('Precio Normal', max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(
        'Precio de Oferta', max_digits=10, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField('Stock Disponible', default=0)

    # --- Imagen (la usaremos en el Paso 3, el campo ya queda listo) ---
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)

    # --- Contenido ---
    descripcion = models.TextField('Descripción Corta')
    instalacion = models.TextField('Uso e Instalación')

    # --- Estado / catálogo (usados por otros tickets del equipo: activar/desactivar, destacar) ---
    activo = models.BooleanField('Activo', default=True)
    destacado_en_inicio = models.BooleanField('Destacado en Inicio', default=False)

    # --- Auditoría ---
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        permissions = []  # No creamos permisos nuevos: reusamos 'Usuarios.gestionar_inventario'

    def __str__(self):
        return f'{self.sku} - {self.nombre}'

    def clean(self):
        # Regla de negocio: si hay precio de oferta, debe ser menor al precio normal
        if self.precio_oferta and self.precio and self.precio_oferta >= self.precio:
            raise ValidationError({
                'precio_oferta': 'El precio de oferta debe ser menor al precio normal.'
            })