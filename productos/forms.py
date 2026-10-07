from django import forms

from .models import Producto, Proveedor
from django.db.models import Q

import re


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'nombre', 'categoria', 'proveedor', 'precio', 'precio_oferta',
            'stock', 'imagen', 'descripcion', 'instalacion',
            'especificaciones',  # NUEVO (HU G1-144)
        ]
        labels = {
            'sku': 'Código (SKU)',
            'nombre': 'Título',
            'categoria': 'Categoría',
            'proveedor': 'Proveedor',
            'precio': 'Precio Normal',
            'precio_oferta': 'Precio de Oferta',
            'stock': 'Stock Disponible',
            'imagen': 'Imagen',
            'descripcion': 'Descripción Corta',
            'instalacion': 'Uso e Instalación',
            'especificaciones': 'Características Técnicas',  # NUEVO
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'instalacion': forms.Textarea(attrs={'rows': 2}),
            # NUEVO: caja de texto más alta, con un ejemplo de cómo llenarla
            'especificaciones': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Potencia: 20W\nVoltaje: 110V\nLúmenes: 1800 lm',
            }),
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
        # Selector de proveedor (como en el Figma)
        self.fields['proveedor'].empty_label = 'Sin proveedor'
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)


class ProveedorForm(forms.ModelForm):
    # Campo extra (no es de la tabla): casillas para vincular varios productos
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.filter(activo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Productos que suministra',
    )

    class Meta:
        model = Proveedor
        fields = ['nombre', 'nit', 'contacto', 'telefono', 'correo', 'direccion', 'activo']
        labels = {
            'nombre': 'Nombre de la empresa *',
            'nit': 'NIT *',
            'contacto': 'Persona de contacto',
            'telefono': 'Teléfono',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
            'activo': 'Proveedor activo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Distribuidora Eléctrica S.A.S.'}),
            'nit': forms.TextInput(attrs={'placeholder': '900123456-7'}),
            'contacto': forms.TextInput(attrs={'placeholder': 'Nombre del contacto'}),
            'telefono': forms.TextInput(attrs={'placeholder': '300 000 0000'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'ventas@proveedor.com'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Calle 10 # 5-20, Sogamoso'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        clase_input = (
            'w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 '
            'rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:outline-none '
            'focus:ring-2 focus:ring-[#F2AE30]'
        )
        for nombre, campo in self.fields.items():
            if nombre not in ('activo', 'productos'):  # checkboxes sin estilo de texto
                campo.widget.attrs['class'] = clase_input
        self.fields['activo'].widget.attrs['class'] = 'w-4 h-4 rounded border-gray-300 text-[#F2AE30] focus:ring-[#F2AE30]'
        
        
        
        
#gv

class ProveedorEditarForm(ProveedorForm):
    """G1-137: edita los datos de contacto. Nombre y NIT no se pueden modificar."""

    class Meta(ProveedorForm.Meta):
        # nombre y nit NO están aquí: el servidor ignora cualquier valor que lleguen en el POST.
        # 'activo' se incluye solo para que el __init__ del padre funcione; se quita abajo
        # (cambiar el estado es otro ticket: G1-138).
        fields = ['contacto', 'telefono', 'correo', 'direccion', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['activo']

        # Se muestran los productos activos + los que ya tiene este proveedor
        # (así, guardar no desvincula por accidente un producto que se inactivó).
        self.fields['productos'].queryset = Producto.objects.filter(
            Q(activo=True) | Q(proveedor=self.instance)
        ).distinct()
        self.initial['productos'] = list(
            self.instance.productos.values_list('pk', flat=True)
        )

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            if not re.fullmatch(r'[\d\s+\-()]+', telefono):
                raise forms.ValidationError(
                    'El teléfono solo puede contener números, espacios, +, - y paréntesis.'
                )
            if not 7 <= len(re.sub(r'\D', '', telefono)) <= 15:
                raise forms.ValidationError('El teléfono debe tener entre 7 y 15 dígitos.')
        return telefono        
    
    


class InactivarProveedorForm(forms.Form):
    """G1-138: valida el motivo obligatorio al inactivar un proveedor."""
    motivo = forms.CharField(
        min_length=5,
        max_length=500,
        error_messages={
            'required': 'Debes indicar el motivo de la inactivación.',
            'min_length': 'El motivo debe tener al menos 5 caracteres.',
            'max_length': 'El motivo no puede superar los 500 caracteres.',
        },
    )