from functools import wraps as preservar_metadados

from django.core.exceptions import PermissionDenied as PermissaoNegada
from django.shortcuts import redirect as redirecionar
from django.urls import reverse as reverter_url


def exige_superusuario(funcao_visao):
    """Restringe uma visão aos superusuários autenticados."""

    @preservar_metadados(funcao_visao)
    def visao_protegida(requisicao, *argumentos, **argumentos_nomeados):
        if not requisicao.user.is_authenticated:
            return redirecionar(f"{reverter_url('inicio')}?autenticacao=entrar")
        if not requisicao.user.is_superuser:
            raise PermissaoNegada("Esta área é restrita a superusuários.")
        return funcao_visao(requisicao, *argumentos, **argumentos_nomeados)

    return visao_protegida
