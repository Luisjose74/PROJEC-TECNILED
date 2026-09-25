from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Usuario
from .forms import CrearUsuarioInternoForm

def inicio(request):
    return render(request, 'inicio.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    error = None
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        error = "Credenciales incorrectas"

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