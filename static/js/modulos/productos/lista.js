// Scripts de la LISTA de productos: DataTables + confirmación de borrado
$(document).ready(function () {

  // DataTables en español
  $('#tabla-productos').DataTable({
    language: {
      url: 'https://cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json'
    }
  });

  // Confirmación de borrado con SweetAlert2
  document.querySelectorAll('.form-eliminar').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var nombre = form.getAttribute('data-nombre');
      Swal.fire({
        title: '¿Eliminar producto?',
        text: 'Vas a eliminar "' + nombre + '". Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      }).then(function (result) {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });

});