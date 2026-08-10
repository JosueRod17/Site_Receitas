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

  const formularioPerfil = document.querySelector('.profile-form');
  const campoEmail = formularioPerfil?.querySelector('#id_email');
  const blocoSenhaAtual = formularioPerfil?.querySelector('#profile-current-password');
  const camposNovaSenha = formularioPerfil?.querySelector('#profile-new-passwords');
  const botaoAlterarSenha = formularioPerfil?.querySelector('#profile-password-button');
  const campoAlteracaoSenha = formularioPerfil?.querySelector('#profile-password-change-requested');

  if (campoEmail && blocoSenhaAtual && camposNovaSenha && botaoAlterarSenha && campoAlteracaoSenha) {
    const emailInicial = campoEmail.defaultValue.trim().toLowerCase();
    let alteracaoSenhaAberta = formularioPerfil.dataset.alteracaoSenhaAberta === 'true';

    const atualizarCamposDeSeguranca = () => {
      const emailFoiAlterado = campoEmail.value.trim().toLowerCase() !== emailInicial;
      blocoSenhaAtual.hidden = !(emailFoiAlterado || alteracaoSenhaAberta);
      camposNovaSenha.hidden = !alteracaoSenhaAberta;
      botaoAlterarSenha.classList.toggle('is-open', alteracaoSenhaAberta);
      botaoAlterarSenha.setAttribute('aria-expanded', String(alteracaoSenhaAberta));
      botaoAlterarSenha.textContent = alteracaoSenhaAberta ? 'Cancelar alteração' : 'Alterar senha';
      campoAlteracaoSenha.value = alteracaoSenhaAberta ? '1' : '0';
    };

    campoEmail.addEventListener('input', atualizarCamposDeSeguranca);
    botaoAlterarSenha.addEventListener('click', () => {
      alteracaoSenhaAberta = !alteracaoSenhaAberta;
      if (!alteracaoSenhaAberta) {
        camposNovaSenha.querySelectorAll('input').forEach((input) => { input.value = ''; });
      }
      atualizarCamposDeSeguranca();
      if (alteracaoSenhaAberta) blocoSenhaAtual.querySelector('input')?.focus();
    });
    atualizarCamposDeSeguranca();
  }

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
