(() => {
  const backdrop = document.querySelector('#modal-backdrop');
  const modals = document.querySelectorAll('.auth-modal, .recipe-modal');
  const openModal = (name) => {
    if (!backdrop) return;
    modals.forEach((modal) => { modal.hidden = modal.id !== `${name}-modal`; });
    backdrop.hidden = false;
    document.body.classList.add('modal-open');
    backdrop.querySelector('input, button:not(.modal-close)')?.focus();
  };
  const closeModal = () => { if (backdrop) { backdrop.hidden = true; document.body.classList.remove('modal-open'); } };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-open-modal]');
    if (trigger) { event.preventDefault(); openModal(trigger.dataset.openModal); }
    if ((backdrop && event.target === backdrop) || event.target.closest('.modal-close')) closeModal();
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeModal(); });

  const requestedModal = new URLSearchParams(window.location.search).get('auth');
  if (requestedModal === 'login' || requestedModal === 'signup') openModal(requestedModal);

  document.querySelectorAll('.auth-form input[type="password"], .profile-form input[type="password"]').forEach((input) => {
    const wrapper = document.createElement('span');
    wrapper.className = 'password-field';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'password-toggle';
    toggle.textContent = 'Mostrar';
    toggle.addEventListener('click', () => {
      const visible = input.type === 'text';
      input.type = visible ? 'password' : 'text';
      toggle.textContent = visible ? 'Mostrar' : 'Ocultar';
    });
    wrapper.appendChild(toggle);
  });

  document.querySelectorAll('.filter-tabs button').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('.filter-tabs button').forEach((tab) => tab.classList.remove('selected'));
    button.classList.add('selected');
  }));
  document.querySelector('#newsletter-form')?.addEventListener('submit', (event) => {
    event.preventDefault();
    event.currentTarget.innerHTML = '<strong>Pronto! Confira seu e-mail.</strong>';
  });
  document.querySelector('#load-more')?.addEventListener('click', (event) => { event.currentTarget.textContent = 'Você chegou ao fim das receitas'; event.currentTarget.disabled = true; });
})();
