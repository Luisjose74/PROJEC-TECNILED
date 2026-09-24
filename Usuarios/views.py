from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login , logout

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