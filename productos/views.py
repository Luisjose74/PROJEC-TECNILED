from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from .forms import ProductoForm


@login_required
@permission_required('Usuarios.gestionar_inventario', raise_exception=True)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" registrado correctamente.')
            return redirect('crear_producto')  # Paso 4: cambiará a 'productos_lista'
    else:
        form = ProductoForm()

    return render(request, 'productos/productos_crear.html', {'form': form})