from django.urls import path

from . import views

urlpatterns = [
    path('productos/crear/', views.crear_producto, name='crear_producto'),
]