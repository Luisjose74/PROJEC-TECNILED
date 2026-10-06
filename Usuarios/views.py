from django.conf import settings
from django.core.mail import send_mail
from .models import CodigoRecuperacion
from .forms import SolicitarRecuperacionForm

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Usuario
from .forms import CrearUsuarioInternoForm, EditarRolForm
from django.shortcuts import get_object_or_404
from productos.models import Producto  # NUEVO: para mostrar productos en el inicio


def inicio(request):
    # NUEVO: productos que el administrador marcó como "Destacado en Inicio" (máximo 4)
    productos_destacados = Producto.objects.filter(
        activo=True, destacado_en_inicio=True
    )[:4]
    return render(request, 'inicio.html', {
        'productos_destacados': productos_destacados,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    error = None
    if request.method == 'POST':
        correo = (request.POST.get('correo') or '').strip().lower()
        contrasena = request.POST.get('contrasena')

        # Buscamos al usuario ANTES de autenticar: si la cuenta está bloqueada,
        # authenticate() devuelve None aunque la clave sea correcta.
        usuario = Usuario.objects.filter(email=correo).first()

        if usuario and usuario.estado_cuenta == Usuario.EstadoCuenta.BLOQUEADA:
            error = "Tu cuenta está bloqueada por intentos fallidos. Contacta al administrador."
        elif usuario and usuario.estado_cuenta == Usuario.EstadoCuenta.SUSPENDIDA:
            error = "Tu cuenta está suspendida. Contacta al administrador."
        else:
            user = authenticate(request, username=correo, password=contrasena)
            if user is not None:
                # Login correcto: se reinicia el contador de intentos
                if user.intentos_fallidos:
                    user.intentos_fallidos = 0
                    user.save()
                login(request, user)
                return redirect('inicio')

            error = "Credenciales incorrectas"
            if usuario:
                usuario.intentos_fallidos += 1
                if usuario.intentos_fallidos >= Usuario.MAX_INTENTOS:
                    usuario.estado_cuenta = Usuario.EstadoCuenta.BLOQUEADA
                    error = "Tu cuenta fue bloqueada por 3 intentos fallidos. Contacta al administrador."
                usuario.save()

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@permission_required('Usuarios.gestionar_usuarios', raise_exception=True)
def usuarios_lista(request):
    query = request.GET.get('q', '').strip()

    usuarios = Usuario.objects.all().order_by('first_name', 'last_name')
    if query:
        usuarios = usuarios.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(documento__icontains=query)
        )

    paginador = Paginator(usuarios, 10)
    pagina = paginador.get_page(request.GET.get('page'))

    return render(request, 'usuarios_lista.html', {
        'usuarios': pagina,
        'query': query,
    })


@login_required
@permission_required('Usuarios.gestionar_usuarios', raise_exception=True)
def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioInternoForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Cuenta creada para {usuario.email}.')
            return redirect('usuarios_lista')
    else:
        form = CrearUsuarioInternoForm()

    return render(request, 'usuarios_crear.html', {'form': form})


@login_required
@permission_required('Usuarios.gestionar_usuarios', raise_exception=True)
def editar_rol(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if request.method == 'POST':
        form = EditarRolForm(request.POST, instance=usuario)
        if form.is_valid():
            if usuario == request.user and form.cleaned_data['rol'] != Usuario.Rol.ADMINISTRADOR:
                form.add_error('rol', 'No puedes quitarte tu propio rol de administrador.')
            else:
                form.save()
                messages.success(request, f'Rol de {usuario.email} actualizado.')
                return redirect('usuarios_lista')
    else:
        form = EditarRolForm(instance=usuario)

    return render(request, 'usuarios_editar_rol.html', {'form': form, 'usuario': usuario})

def recuperar_contrasena(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = SolicitarRecuperacionForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo'].strip().lower()
            usuario = Usuario.objects.filter(email=correo).first()
            # Solo cuentas activas reciben código (las bloqueadas no se saltan el bloqueo)
            if usuario and usuario.estado_cuenta == Usuario.EstadoCuenta.ACTIVA:
                _, codigo = CodigoRecuperacion.generar(usuario)
                send_mail(
                    subject='Código de recuperación - TECNILED',
                    message=(
                        f'Hola {usuario.first_name or usuario.email},\n\n'
                        f'Tu código de recuperación es: {codigo}\n'
                        f'Es válido por {CodigoRecuperacion.VIGENCIA_MINUTOS} minutos y solo se puede usar una vez.\n\n'
                        'Si no lo solicitaste, ignora este mensaje.'
                    ),
                    from_email=None,
                    recipient_list=[usuario.email],
                )
            # Mismo mensaje exista o no el correo (no revela qué cuentas existen)
            request.session['recuperacion_correo'] = correo
            messages.success(request, 'Si el correo está registrado, te enviamos un código de recuperación.')
            return redirect('login')  # provisional: en el PASO 3 irá a la pantalla del código
    else:
        form = SolicitarRecuperacionForm()

    return render(request, 'recuperar_contrasena.html', {'form': form})