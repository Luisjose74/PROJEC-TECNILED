from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from productos.models import Producto, Proveedor


class OrdenCompra(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        RECIBIDA = 'recibida', 'Recibida'
        ANULADA = 'anulada', 'Anulada'

    numero_factura = models.CharField('Número de orden/factura', max_length=30, unique=True)
    fecha = models.DateField('Fecha', default=timezone.localdate)
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, related_name='ordenes_compra',
    )
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE,
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # --- Auditoría ---
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name = 'orden de compra'
        verbose_name_plural = 'órdenes de compra'

    def __str__(self):
        return f'Orden {self.numero_factura} - {self.proveedor}'

    def clean(self):
        # G1-132: no se puede asociar un proveedor inactivo a una orden NUEVA.
        # (Si la orden ya existe, se permite que su proveedor quede inactivo después.)
        if self._state.adding and self.proveedor_id and not self.proveedor.activo:
            raise ValidationError({
                'proveedor': 'No puedes asociar un proveedor inactivo a una orden de compra.'
            })

    def calcular_total(self):
        """Suma los subtotales de todas las líneas y guarda el resultado."""
        self.total = sum(
            (linea.subtotal for linea in self.detalles.all()), Decimal('0')
        )
        self.save(update_fields=['total', 'actualizado_en'])
        return self.total

    @property
    def es_editable(self):
        """Solo las órdenes pendientes se pueden modificar (lo usan otros tickets)."""
        return self.estado == self.Estado.PENDIENTE


class DetalleOrdenCompra(models.Model):
    orden = models.ForeignKey(
        OrdenCompra, on_delete=models.CASCADE, related_name='detalles',
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name='detalles_compra',
    )
    cantidad = models.PositiveIntegerField('Cantidad')
    precio_unitario = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'línea de la orden'
        verbose_name_plural = 'líneas de la orden'

    def __str__(self):
        return f'{self.producto.sku} x {self.cantidad}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def clean(self):
        if self.cantidad is not None and self.cantidad < 1:
            raise ValidationError({'cantidad': 'La cantidad debe ser al menos 1.'})
        if self.precio_unitario is not None and self.precio_unitario <= 0:
            raise ValidationError({'precio_unitario': 'El precio unitario debe ser mayor que 0.'})