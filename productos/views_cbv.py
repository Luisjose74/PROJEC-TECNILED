from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Proveedor


# ───── LISTAR (ListView) ─────
class ProveedorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Proveedor
    template_name = "productos/cbv/proveedor_lista.html"
    context_object_name = "proveedores"
    paginate_by = 10
    permission_required = "Usuarios.gestionar_compras"


# ───── CREAR (CreateView) ─────
class ProveedorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Proveedor
    fields = ["nombre", "nit", "contacto", "telefono", "correo", "direccion", "activo"]
    template_name = "productos/cbv/proveedor_form.html"
    success_url = reverse_lazy("cbv_proveedores_lista")
    permission_required = "Usuarios.gestionar_compras"


# ───── EDITAR (UpdateView) ─────
class ProveedorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Proveedor
    fields = ["nombre", "nit", "contacto", "telefono", "correo", "direccion", "activo"]
    template_name = "productos/cbv/proveedor_form.html"
    success_url = reverse_lazy("cbv_proveedores_lista")
    permission_required = "Usuarios.gestionar_compras"


# ───── ELIMINAR (DeleteView) ─────
class ProveedorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Proveedor
    template_name = "productos/cbv/proveedor_confirmar_eliminar.html"
    success_url = reverse_lazy("cbv_proveedores_lista")
    permission_required = "Usuarios.gestionar_compras"
