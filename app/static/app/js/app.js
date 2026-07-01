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
  // MODAL DE NUEVA PARTIDA
  // =========================
  const newGameModal = document.querySelector('[data-new-game-modal]');
  const openNewGame = document.querySelector('[data-open-new-game]');
  const closeNewGame = document.querySelector('[data-close-new-game]');

  if (newGameModal && openNewGame) {
    openNewGame.addEventListener('click', () => {
      if (typeof newGameModal.showModal === 'function') {
        newGameModal.showModal();
      }
    });

    newGameModal.addEventListener('click', (event) => {
      if (event.target === newGameModal) {
        newGameModal.close();
      }
    });
  }

  if (newGameModal && closeNewGame) {
    closeNewGame.addEventListener('click', () => {
      newGameModal.close();
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
