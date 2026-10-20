from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Replace
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import InactivarProveedorForm, ProductoForm, ProveedorEditarForm, ProveedorForm
from .models import Producto, Proveedor


@login_required
@permission_required('Usuarios.gestionar_inventario', raise_exception=True)
def productos_lista(request):
    query = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    productos = Producto.objects.select_related('proveedor')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(sku__icontains=query)
        )

    if categoria in Producto.Categoria.values:
        productos = productos.filter(categoria=categoria)
    else:
        categoria = ''  # valor manipulado en la URL: se ignora

    paginador = Paginator(productos, 10)
    pagina = paginador.get_page(request.GET.get('page'))

    return render(request, 'productos/productos_lista.html', {
        'productos': pagina,
        'query': query,
        'categoria': categoria,
        'categorias': Producto.Categoria.choices,
    })


@login_required
@permission_required('Usuarios.gestionar_inventario', raise_exception=True)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" registrado correctamente.')
            return redirect('productos_lista')
    else:
        form = ProductoForm()

    return render(request, 'productos/productos_crear.html', {'form': form})


@login_required
@permission_required('Usuarios.gestionar_inventario', raise_exception=True)
@require_POST
def alternar_destacado(request, producto_id):
    """Activa/desactiva 'Destacado en Inicio' (interruptor verde de la tabla)."""
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.destacado_en_inicio = not producto.destacado_en_inicio
    producto.save(update_fields=['destacado_en_inicio', 'actualizado_en'])

    # Volver a la misma página, con la búsqueda/filtro/paginación que tenía.
    # Solo se acepta una ruta interna del propio sitio.
    siguiente = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        siguiente = reverse('productos_lista')
    return redirect(siguiente)


def producto_detalle(request, producto_id):
    # Página pública: la ve cualquier cliente, por eso NO lleva @login_required

    # 1) Buscar el producto que el usuario quiere ver
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)

    # 2) Buscar productos relacionados (misma categoría, sin repetir este, máximo 2)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria, activo=True
    ).exclude(pk=producto.pk)[:2]

    # 3) Enviar las dos cosas a la plantilla
    return render(request, 'productos/producto_detalle.html', {
        'producto': producto,
        'relacionados': relacionados,
    })


@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
def proveedores_lista(request):
    query = request.GET.get('q', '').strip()
    proveedores = Proveedor.objects.prefetch_related('productos')

    if query:
        # G1-134: busca por nombre o NIT. El NIT también se encuentra si se escribe
        # sin guiones, puntos ni espacios (ej: 9001234567 encuentra 900123456-7).
        nit_buscado = query.replace('-', '').replace('.', '').replace(' ', '')
        filtro = Q(nombre__icontains=query) | Q(nit__icontains=query)
        if nit_buscado:
            proveedores = proveedores.annotate(
                nit_limpio=Replace(
                    Replace(Replace('nit', Value('-'), Value('')), Value('.'), Value('')),
                    Value(' '), Value(''),
                )
            )
            filtro |= Q(nit_limpio__icontains=nit_buscado)
        proveedores = proveedores.filter(filtro)

    pagina = Paginator(proveedores, 10).get_page(request.GET.get('page'))
    return render(request, 'productos/proveedores_lista.html', {
        'proveedores': pagina,
        'query': query,
    })


@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            elegidos = form.cleaned_data['productos']
            # Los desmarcados quedan sin proveedor; los marcados pasan a este proveedor
            proveedor.productos.exclude(pk__in=elegidos).update(proveedor=None)
            elegidos.update(proveedor=proveedor)
            messages.success(request, f'Proveedor "{proveedor.nombre}" registrado correctamente.')
            return redirect('proveedores_lista')
    else:
        form = ProveedorForm()

    return render(request, 'productos/proveedores_crear.html', {'form': form})




@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
def editar_proveedor(request, pk):
    """G1-137: actualiza contacto/dirección/correo. Nombre y NIT no se modifican."""
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        form = ProveedorEditarForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            elegidos = form.cleaned_data['productos']
            # Los desmarcados quedan sin proveedor; los marcados pasan a este proveedor
            proveedor.productos.exclude(pk__in=elegidos).update(proveedor=None)
            elegidos.update(proveedor=proveedor)
            messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado correctamente.')
            return redirect('proveedores_lista')
    else:
        form = ProveedorEditarForm(instance=proveedor)

    return render(request, 'productos/proveedores_crear.html', {
        'form': form,
        'proveedor': proveedor,  # su presencia activa el "modo edición" en la plantilla
    })
    
    
    


@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
@require_POST
def inactivar_proveedor(request, pk):
    """G1-138: inactiva un proveedor registrando el motivo. No elimina nada."""
    proveedor = get_object_or_404(Proveedor, pk=pk)

    # Volver a la misma página de la lista (con su búsqueda/paginación).
    # Solo se acepta una ruta interna del propio sitio.
    siguiente = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        siguiente = reverse('proveedores_lista')

    if not proveedor.activo:
        messages.error(request, f'El proveedor "{proveedor.nombre}" ya está inactivo.')
        return redirect(siguiente)

    form = InactivarProveedorForm(request.POST)
    if not form.is_valid():
        messages.error(request, form.errors['motivo'][0])
        return redirect(siguiente)

    proveedor.inactivar(form.cleaned_data['motivo'])
    messages.success(request, f'Proveedor "{proveedor.nombre}" inactivado correctamente.')
    return redirect(siguiente)




@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
@require_POST
def reactivar_proveedor(request, pk):
    """Vuelve a activar un proveedor que había sido inactivado."""
    proveedor = get_object_or_404(Proveedor, pk=pk)

    siguiente = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        siguiente = reverse('proveedores_lista')

    if proveedor.activo:
        messages.error(request, f'El proveedor "{proveedor.nombre}" ya está activo.')
        return redirect(siguiente)

    proveedor.reactivar()
    messages.success(request, f'Proveedor "{proveedor.nombre}" reactivado correctamente.')
    return redirect(siguiente)