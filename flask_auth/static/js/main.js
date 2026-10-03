// Cerrar mensajes flash
document.querySelectorAll('.flash-close').forEach(function (btn) {
  btn.addEventListener('click', function () { btn.parentElement.remove(); });
});

// Confirmación antes de enviar formularios con data-confirm (p. ej. eliminar cuenta)
document.querySelectorAll('form[data-confirm]').forEach(function (form) {
  form.addEventListener('submit', function (e) {
    if (!window.confirm(form.dataset.confirm)) { e.preventDefault(); }
  });
});
