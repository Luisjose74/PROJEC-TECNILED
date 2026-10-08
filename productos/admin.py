from django import forms
from django.contrib import admin

from .models import Producto, Proveedor


class ProveedorAdminForm(forms.ModelForm):
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Productos que suministra',
    )

    class Meta:
        model = Proveedor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['productos'].initial = self.instance.productos.all()


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    form = ProveedorAdminForm
    list_display = ('nombre', 'nit', 'telefono', 'activo', 'total_productos')
    search_fields = ('nombre', 'nit')

    @admin.display(description='Productos')
    def total_productos(self, obj):
        return obj.productos.count()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        proveedor = form.instance
        elegidos = form.cleaned_data['productos']
        # Los desmarcados quedan sin proveedor; los marcados pasan a este proveedor
        proveedor.productos.exclude(pk__in=elegidos).update(proveedor=None)
        elegidos.update(proveedor=proveedor)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'proveedor', 'precio', 'precio_oferta', 'stock', 'activo')
    list_filter = ('categoria', 'proveedor', 'activo', 'destacado_en_inicio')
    search_fields = ('sku', 'nombre')
    ordering = ('nombre',)