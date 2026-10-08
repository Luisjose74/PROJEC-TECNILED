from django.urls import path
from . import views

urlpatterns = [
    path('respaldos/', views.lista_respaldos, name='respaldos_lista'),
    path('respaldos/generar/', views.generar_respaldo, name='respaldos_generar'),
    path('respaldos/<int:pk>/descargar/', views.descargar_respaldo, name='respaldos_descargar'),
    path('respaldos/<int:pk>/restaurar/', views.restaurar_respaldo, name='respaldos_restaurar'),
]