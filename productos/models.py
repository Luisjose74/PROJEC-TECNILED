from django.core.exceptions import ValidationError
from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    nit = models.CharField('NIT', max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    contacto = models.CharField('Persona de contacto', max_length=100, blank=True)
    direccion = models.CharField('Dirección', max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


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
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT,
        null=True, blank=True, related_name='productos',
    )
    precio = models.DecimalField('Precio Normal', max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(
        'Precio de Oferta', max_digits=10, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField('Stock Disponible', default=0)

    # --- Imagen ---
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)

    # --- Contenido ---
    descripcion = models.TextField('Descripción Corta')
    instalacion = models.TextField('Uso e Instalación')

    especificaciones = models.TextField(
        'Características Técnicas', blank=True,
        help_text='Una característica por línea. Ejemplo: Potencia: 20W',
    )

    # --- Estado / catálogo ---
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

    def porcentaje_descuento(self):
        """Devuelve el % de descuento (ej: 23) o 0 si no tiene oferta."""
        if self.precio_oferta and self.precio:
            descuento = (self.precio - self.precio_oferta) / self.precio * 100
            return round(descuento)
        return 0

    def lista_especificaciones(self):
        """Convierte el texto de especificaciones en una lista de (nombre, valor)."""
        lista = []
        for linea in self.especificaciones.splitlines():
            linea = linea.strip()
            if linea == '':
                continue
            if ':' in linea:
                nombre, valor = linea.split(':', 1)
                lista.append((nombre.strip(), valor.strip()))
            else:
                lista.append(('', linea))
        return lista

    def clean(self):
        # Regla de negocio: si hay precio de oferta, debe ser menor al precio normal
        if self.precio_oferta and self.precio and self.precio_oferta >= self.precio:
            raise ValidationError({
                'precio_oferta': 'El precio de oferta debe ser menor al precio normal.'
            })