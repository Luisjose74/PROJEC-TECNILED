from django.urls import path

from . import views
from . import views_cbv

urlpatterns = [
    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/<int:producto_id>/destacar/', views.alternar_destacado, name='alternar_destacado'),
    path('productos/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('proveedores/', views.proveedores_lista, name='proveedores_lista'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:pk>/inactivar/', views.inactivar_proveedor, name='inactivar_proveedor'),
    path('proveedores/<int:pk>/reactivar/', views.reactivar_proveedor, name='reactivar_proveedor'),
        # ───── CRUD de Proveedores con CBV (A3) ─────
    path('proveedores-cbv/', views_cbv.ProveedorListView.as_view(), name='cbv_proveedores_lista'),
    path('proveedores-cbv/crear/', views_cbv.ProveedorCreateView.as_view(), name='cbv_proveedor_crear'),
    path('proveedores-cbv/<int:pk>/editar/', views_cbv.ProveedorUpdateView.as_view(), name='cbv_proveedor_editar'),
    path('proveedores-cbv/<int:pk>/eliminar/', views_cbv.ProveedorDeleteView.as_view(), name='cbv_proveedor_eliminar'),

]