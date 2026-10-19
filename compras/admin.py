from django.contrib import admin

from .models import DetalleOrdenCompra, OrdenCompra


class DetalleInline(admin.TabularInline):
    model = DetalleOrdenCompra
    extra = 1


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'fecha', 'proveedor', 'estado', 'total')
    list_filter = ('estado', 'fecha')
    search_fields = ('numero_factura', 'proveedor__nombre')
    inlines = [DetalleInline]