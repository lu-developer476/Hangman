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
  // BARRAS LATERALES DESPLEGABLES
  // =========================
  const rails = document.querySelectorAll('[data-collapsible-rail]');

  rails.forEach((rail) => {
    const toggle = rail.querySelector('.rail-toggle');
    const toggleIcon = rail.querySelector('.rail-toggle-icon');
    const side = rail.dataset.railSide;

    if (!toggle) return;

    toggle.addEventListener('click', () => {
      const isCollapsed = rail.classList.toggle('is-collapsed');
      toggle.setAttribute('aria-expanded', String(!isCollapsed));

      if (toggleIcon) {
        toggleIcon.textContent = isCollapsed
          ? (side === 'left' ? '›' : '‹')
          : (side === 'left' ? '‹' : '›');
      }
    });
  });

  // =========================
  // FOOTER - AÑO AUTOMÁTICO
  // =========================
  const year = document.querySelector('#year');

  if (year) {
    year.textContent = new Date().getFullYear();
  }
});
