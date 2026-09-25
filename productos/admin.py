from django.contrib import admin

from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'precio', 'precio_oferta', 'stock', 'activo')
    list_filter = ('categoria', 'activo', 'destacado_en_inicio')
    search_fields = ('sku', 'nombre')
    ordering = ('nombre',)
    
    list_display = ('sku', 'nombre', 'categoria', 'precio', 'precio_oferta', 'stock', 'activo', 'imagen')