document.addEventListener('DOMContentLoaded', () => {
  const input = document.querySelector('#letter');
  if (!input) return;

  input.addEventListener('input', () => {
    input.value = input.value.replace(/[^a-zA-Z]/g, '').slice(0, 1);
  });
});
