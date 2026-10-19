from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import DetalleFormSet, OrdenCompraForm
from .models import OrdenCompra


def _interpretar_fecha(texto):
    """Devuelve una fecha si el texto parece una (2026-10-14 o 14/10/2026); si no, None."""
    for formato in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
def ordenes_lista(request):
    """G1-160: lista las órdenes y permite buscar por factura, fecha o proveedor."""
    query = request.GET.get('q', '').strip()
    ordenes = OrdenCompra.objects.select_related('proveedor')

    if query:
        filtro = Q(numero_factura__icontains=query) | Q(proveedor__nombre__icontains=query)
        fecha = _interpretar_fecha(query)
        if fecha:
            filtro |= Q(fecha=fecha)
        ordenes = ordenes.filter(filtro)

    pagina = Paginator(ordenes, 10).get_page(request.GET.get('page'))
    return render(request, 'compras/ordenes_lista.html', {
        'ordenes': pagina,
        'query': query,
    })


@login_required
@permission_required('Usuarios.gestionar_compras', raise_exception=True)
def crear_orden(request):
    """G1-158 / G1-132: registra una orden de compra con sus productos."""
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST)
        formset = DetalleFormSet(request.POST)
        # Se validan los dos SIEMPRE, así se muestran todos los errores juntos
        cabecera_ok = form.is_valid()
        lineas_ok = formset.is_valid()
        if cabecera_ok and lineas_ok:
            # atomic: o se guarda todo (orden + líneas + total) o no se guarda nada
            with transaction.atomic():
                orden = form.save()          # estado queda en "Pendiente"
                formset.instance = orden
                formset.save()
                orden.calcular_total()
            messages.success(
                request, f'Orden "{orden.numero_factura}" registrada correctamente.'
            )
            return redirect('ordenes_lista')
    else:
        form = OrdenCompraForm()
        formset = DetalleFormSet()

    return render(request, 'compras/orden_crear.html', {
        'form': form,
        'formset': formset,
    })