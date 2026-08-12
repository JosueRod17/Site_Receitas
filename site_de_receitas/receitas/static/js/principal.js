(() => {
  const fundoModal = document.querySelector('#fundo-modal');
  const modais = document.querySelectorAll('.modal-autenticacao, .modal-receita');
  const identificadoresDosModais = {
    entrar: 'modal-entrar',
    cadastro: 'modal-cadastro',
    receita: 'modal-receita',
  };
  // Mantém os redirecionamentos atuais funcionando até as rotas serem renomeadas.
  const abrirModal = (nome) => {
    const identificadorDoModal = identificadoresDosModais[nome];
    if (!fundoModal || !identificadorDoModal) return;

    modais.forEach((modal) => { modal.hidden = modal.id !== identificadorDoModal; });
    fundoModal.hidden = false;
    document.body.classList.add('modal-aberto');
    fundoModal.querySelector('input, button:not(.botao-fechar-modal)')?.focus();
  };

  const fecharModal = () => {
    if (!fundoModal) return;

    fundoModal.hidden = true;
    document.body.classList.remove('modal-aberto');
  };

  document.addEventListener('click', (evento) => {
    const acionador = evento.target.closest('[data-abrir-modal]');
    if (acionador) {
      evento.preventDefault();
      abrirModal(acionador.dataset.abrirModal);
    }
    if ((fundoModal && evento.target === fundoModal) || evento.target.closest('.botao-fechar-modal')) {
      fecharModal();
    }
  });
  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape') fecharModal();
  });

  const modalSolicitado = new URLSearchParams(window.location.search).get('autenticacao');
  if (modalSolicitado) abrirModal(modalSolicitado);

  document.querySelectorAll('.formulario-autenticacao input[type="password"], .formulario-perfil input[type="password"]').forEach((campo) => {
    const recipiente = document.createElement('span');
    recipiente.className = 'campo-senha';
    campo.parentNode.insertBefore(recipiente, campo);
    recipiente.appendChild(campo);

    const botaoAlternar = document.createElement('button');
    botaoAlternar.type = 'button';
    botaoAlternar.className = 'botao-alternar-senha';
    botaoAlternar.textContent = 'Mostrar';
    botaoAlternar.addEventListener('click', () => {
      const estaVisivel = campo.type === 'text';
      campo.type = estaVisivel ? 'password' : 'text';
      botaoAlternar.textContent = estaVisivel ? 'Mostrar' : 'Ocultar';
    });
    recipiente.appendChild(botaoAlternar);
  });

  const formularioPerfil = document.querySelector('.formulario-perfil');
  const campoApelido = formularioPerfil?.querySelector('input[name="apelido"]');
  const campoNomeUsuario = formularioPerfil?.querySelector('input[name="nome_usuario"]');
  const campoEmail = formularioPerfil?.querySelector('input[name="email"]');
  const blocoSenhaAtual = formularioPerfil?.querySelector('#perfil-senha-atual');
  const camposNovaSenha = formularioPerfil?.querySelector('#perfil-novas-senhas');
  const botaoAlterarSenha = formularioPerfil?.querySelector('#botao-alterar-senha-perfil');
  const campoAlteracaoSenha = formularioPerfil?.querySelector('#alteracao-senha-solicitada');

  if (campoApelido && campoNomeUsuario && campoEmail && blocoSenhaAtual && camposNovaSenha && botaoAlterarSenha && campoAlteracaoSenha) {
    const apelidoInicial = campoApelido.defaultValue.trim();
    const nomeUsuarioInicial = campoNomeUsuario.defaultValue.trim().toLowerCase();
    const emailInicial = campoEmail.defaultValue.trim().toLowerCase();
    let alteracaoSenhaAberta = formularioPerfil.dataset.alteracaoSenhaAberta === 'true';
    const senhaAtualDeveFicarVisivel = formularioPerfil.dataset.senhaAtualVisivel === 'true';

    const atualizarCamposDeSeguranca = () => {
      const apelidoFoiAlterado = campoApelido.value.trim() !== apelidoInicial;
      const nomeUsuarioFoiAlterado = campoNomeUsuario.value.trim().toLowerCase() !== nomeUsuarioInicial;
      const emailFoiAlterado = campoEmail.value.trim().toLowerCase() !== emailInicial;
      blocoSenhaAtual.hidden = !(apelidoFoiAlterado || nomeUsuarioFoiAlterado || emailFoiAlterado || alteracaoSenhaAberta || senhaAtualDeveFicarVisivel);
      camposNovaSenha.hidden = !alteracaoSenhaAberta;
      botaoAlterarSenha.classList.toggle('esta-aberto', alteracaoSenhaAberta);
      botaoAlterarSenha.setAttribute('aria-expanded', String(alteracaoSenhaAberta));
      botaoAlterarSenha.textContent = alteracaoSenhaAberta ? 'Cancelar alteração' : 'Alterar senha';
      campoAlteracaoSenha.value = alteracaoSenhaAberta ? '1' : '0';
    };

    campoApelido.addEventListener('input', atualizarCamposDeSeguranca);
    campoNomeUsuario.addEventListener('input', atualizarCamposDeSeguranca);
    campoEmail.addEventListener('input', atualizarCamposDeSeguranca);
    botaoAlterarSenha.addEventListener('click', () => {
      alteracaoSenhaAberta = !alteracaoSenhaAberta;
      if (!alteracaoSenhaAberta) {
        camposNovaSenha.querySelectorAll('input').forEach((campo) => { campo.value = ''; });
      }
      atualizarCamposDeSeguranca();
      if (alteracaoSenhaAberta) blocoSenhaAtual.querySelector('input')?.focus();
    });
    atualizarCamposDeSeguranca();
  }

  document.querySelectorAll('.abas-filtro button').forEach((botao) => botao.addEventListener('click', () => {
    document.querySelectorAll('.abas-filtro button').forEach((aba) => aba.classList.remove('selecionado'));
    botao.classList.add('selecionado');
  }));
  document.querySelector('#formulario-novidades')?.addEventListener('submit', (evento) => {
    evento.preventDefault();
    evento.currentTarget.innerHTML = '<strong>Pronto! Confira seu e-mail.</strong>';
  });
  document.querySelector('#carregar-mais')?.addEventListener('click', (evento) => {
    evento.currentTarget.textContent = 'Você chegou ao fim das receitas';
    evento.currentTarget.disabled = true;
  });
})();
