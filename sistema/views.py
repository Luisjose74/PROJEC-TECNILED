from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import respaldos as servicio
from .models import RegistroRespaldo

CONFIRMACION = 'RESTAURAR'


def solo_admin(vista):
    """Anónimo -> login; sin permiso -> 403."""
    return login_required(
        permission_required('sistema.gestionar_respaldos', raise_exception=True)(vista)
    )


@solo_admin
def lista_respaldos(request):
    respaldos = list(RegistroRespaldo.objects.all())
    for r in respaldos:
        r.disponible = servicio.archivo_disponible(r)
    return render(request, 'sistema/respaldos.html', {'respaldos': respaldos})


@solo_admin
@require_POST
def generar_respaldo(request):
    r = servicio.crear_respaldo('manual', request.user)
    if r.estado == 'exitoso':
        messages.success(request, f'Copia de seguridad creada: {Path(r.ruta_archivo).name}')
    else:
        messages.error(request, 'No se pudo generar la copia de seguridad. Revisa el historial.')
    return redirect('respaldos_lista')


@solo_admin
def descargar_respaldo(request, pk):
    r = get_object_or_404(RegistroRespaldo, pk=pk)
    if not servicio.archivo_disponible(r):
        messages.error(request, 'El archivo de este respaldo ya no está disponible.')
        return redirect('respaldos_lista')
    ruta = Path(r.ruta_archivo)
    return FileResponse(open(ruta, 'rb'), as_attachment=True, filename=ruta.name)


@solo_admin
def restaurar_respaldo(request, pk):
    r = get_object_or_404(RegistroRespaldo, pk=pk)
    if not servicio.archivo_disponible(r):
        messages.error(request, 'El archivo de este respaldo ya no está disponible.')
        return redirect('respaldos_lista')

    if request.method == 'POST':
        if request.POST.get('confirmacion', '').strip().lower() != CONFIRMACION.lower():
            messages.error(request, f'Debes escribir {CONFIRMACION} para confirmar.')
        else:
            try:
                servicio.restaurar_respaldo(r, request.user)
                messages.success(request, 'Sistema restaurado correctamente.')
                return redirect('respaldos_lista')
            except servicio.RespaldoError as exc:
                messages.error(request, str(exc))
    return render(request, 'sistema/respaldo_restaurar.html', {'respaldo': r})