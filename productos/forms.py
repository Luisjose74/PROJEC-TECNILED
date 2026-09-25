from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'nombre', 'categoria', 'precio', 'precio_oferta',
            'stock', 'imagen', 'descripcion', 'instalacion',
        ]
        labels = {
            'sku': 'Código (SKU)',
            'nombre': 'Título',
            'categoria': 'Categoría',
            'precio': 'Precio Normal',
            'precio_oferta': 'Precio de Oferta',
            'stock': 'Stock Disponible',
            'imagen': 'Imagen',
            'descripcion': 'Descripción Corta',
            'instalacion': 'Uso e Instalación',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'instalacion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        clase_input = (
            'w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 '
            'rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:outline-none '
            'focus:ring-2 focus:ring-[#F2AE30]'
        )
        for campo in self.fields.values():
            campo.widget.attrs['class'] = clase_input
        # El input de archivo no debe llevar el mismo padding que un texto
        self.fields['imagen'].widget.attrs['class'] = 'hidden'
        self.fields['imagen'].widget.attrs['id'] = 'id_imagen'
        self.fields['imagen'].required = False