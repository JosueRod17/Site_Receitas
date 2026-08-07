(() => {
  const backdrop = document.querySelector('#modal-backdrop');
  const modals = document.querySelectorAll('.auth-modal, .recipe-modal');
  const openModal = (name) => {
    modals.forEach((modal) => { modal.hidden = modal.id !== `${name}-modal`; });
    backdrop.hidden = false;
    document.body.classList.add('modal-open');
    backdrop.querySelector('input, button:not(.modal-close)')?.focus();
  };
  const closeModal = () => { backdrop.hidden = true; document.body.classList.remove('modal-open'); };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-open-modal]');
    if (trigger) { event.preventDefault(); openModal(trigger.dataset.openModal); }
    if (event.target === backdrop || event.target.closest('.modal-close')) closeModal();
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeModal(); });

  document.querySelectorAll('.recipe-card').forEach((card) => {
    const showRecipe = () => { document.querySelector('#recipe-modal-title').textContent = card.dataset.recipe; openModal('recipe'); };
    card.addEventListener('click', showRecipe);
    card.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); showRecipe(); } });
  });
  document.querySelectorAll('.filter-tabs button').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('.filter-tabs button').forEach((tab) => tab.classList.remove('selected'));
    button.classList.add('selected');
  }));
  document.querySelector('#newsletter-form').addEventListener('submit', (event) => {
    event.preventDefault();
    event.currentTarget.innerHTML = '<strong>Pronto! Confira seu e-mail.</strong>';
  });
  document.querySelector('#load-more').addEventListener('click', (event) => { event.currentTarget.textContent = 'Você chegou ao fim das receitas'; event.currentTarget.disabled = true; });
})();
