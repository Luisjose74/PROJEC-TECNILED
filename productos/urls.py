from django.urls import path

from . import views

urlpatterns = [
    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/destacar/', views.alternar_destacado, name='alternar_destacado'),
]