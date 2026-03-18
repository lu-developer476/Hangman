document.addEventListener('DOMContentLoaded', () => {
  // =========================
  // INPUT DE LETRA (VALIDACIÓN)
  // =========================
  const input = document.querySelector('#letter');

  if (input) {
    input.addEventListener('input', () => {
      input.value = input.value
        .toLowerCase()
        .normalize('NFD') // separa acentos
        .replace(/[^a-zñ]/g, '') // permite letras + ñ
        .slice(0, 1); // máximo 1 carácter
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
