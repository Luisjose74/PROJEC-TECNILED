from django.contrib import admin
from .models import Producto, Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono', 'activo')
    search_fields = ('nombre', 'nit')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'proveedor', 'precio', 'precio_oferta', 'stock', 'activo')
    list_filter = ('categoria', 'proveedor', 'activo', 'destacado_en_inicio')
    search_fields = ('sku', 'nombre')
    ordering = ('nombre',)