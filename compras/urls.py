from django.urls import path

from . import views

urlpatterns = [
    path('compras/', views.ordenes_lista, name='ordenes_lista'),
    path('compras/crear/', views.crear_orden, name='crear_orden'),
]