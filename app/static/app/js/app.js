document.addEventListener('DOMContentLoaded', () => {
  // =========================
  // INPUT DE LETRA (VALIDACIÓN)
  // =========================
  const input = document.querySelector('#letter');

  if (input) {
    input.addEventListener('input', () => {
      input.value = input.value
        .replace(/[^a-zA-Z]/g, '') // sólo letras
        .slice(0, 1);              // máximo 1 carácter
    });
  }

  // =========================
  // FOOTER - AÑO AUTOMÁTICO
  // =========================
  const year = document.querySelector('#year');

  if (year) {
    year.textContent = new Date().getFullYear();
  }
});
