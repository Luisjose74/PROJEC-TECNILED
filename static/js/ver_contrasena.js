// Muestra u oculta la contraseña al hacer clic en el botón del ojo.
// Se usa en el login y en el formulario de crear usuario.
function verContrasena(idCampo, boton) {
  var campo = document.getElementById(idCampo);
  var ojo = boton.querySelector('.icono-ojo');
  var ojoTachado = boton.querySelector('.icono-ojo-tachado');

  if (campo.type === 'password') {
    // Estaba oculta: la mostramos
    campo.type = 'text';
    ojo.classList.add('hidden');
    ojoTachado.classList.remove('hidden');
    boton.setAttribute('aria-label', 'Ocultar contraseña');
    boton.title = 'Ocultar contraseña';
  } else {
    // Estaba visible: la ocultamos
    campo.type = 'password';
    ojo.classList.remove('hidden');
    ojoTachado.classList.add('hidden');
    boton.setAttribute('aria-label', 'Mostrar contraseña');
    boton.title = 'Mostrar contraseña';
  }
}