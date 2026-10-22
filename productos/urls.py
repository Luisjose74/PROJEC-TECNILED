from django.urls import path

from . import views

urlpatterns = [
    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/desactivar/', views.cambiar_estado_producto, {'activar': False}, name='desactivar_producto'),
    path('productos/<int:pk>/activar/', views.cambiar_estado_producto, {'activar': True}, name='activar_producto'),
    path('productos/<int:producto_id>/destacar/', views.alternar_destacado, name='alternar_destacado'),
    path('productos/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('proveedores/', views.proveedores_lista, name='proveedores_lista'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:pk>/inactivar/', views.inactivar_proveedor, name='inactivar_proveedor'),
    path('proveedores/<int:pk>/reactivar/', views.reactivar_proveedor, name='reactivar_proveedor'),
]