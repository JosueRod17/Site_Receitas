from django.contrib import messages as mensagens
from django.contrib.auth import authenticate as autenticar
from django.contrib.auth import login as iniciar_sessao
from django.contrib.auth import logout as encerrar_sessao
from django.contrib.auth import update_session_auth_hash as atualizar_hash_sessao
from django.contrib.auth.decorators import login_required as exige_login
from django.contrib.auth.models import User as Usuario
from django.db.models import Avg as Media
from django.db.models import Count as Contagem
from django.db.models import Q as Ou
from django.shortcuts import get_object_or_404 as obter_ou_404
from django.shortcuts import redirect as redirecionar
from django.shortcuts import render as renderizar
from django.urls import reverse as reverter_url
from django.utils.http import url_has_allowed_host_and_scheme as url_permitida

from .formularios import (
    FormularioAvaliacaoReceita,
    FormularioCadastro,
    FormularioPerfil,
)
from .modelos import Avaliacao, Favorito, Receita


def receitas_com_media_avaliacoes():
    return Receita.objects.annotate(
        media_avaliacoes=Media("avaliacoes__nota"),
        total_avaliacoes=Contagem("avaliacoes"),
    )


def receitas_filtradas(requisicao):
    busca = requisicao.GET.get("busca", "").strip()
    categoria = requisicao.GET.get("categoria", "").strip()
    ordenacao = requisicao.GET.get("ordenacao", "recentes")
    receitas = receitas_com_media_avaliacoes()
    if busca:
        receitas = receitas.filter(
            Ou(titulo__icontains=busca) | Ou(categoria__icontains=busca)
        )
    if categoria:
        receitas = receitas.filter(categoria=categoria)
    criterio_ordenacao = {
        "faceis": "tempo_preparo",
        "melhor_avaliadas": "-media_avaliacoes",
    }.get(ordenacao, "-criada_em")
    return receitas.order_by(criterio_ordenacao), busca, categoria, ordenacao


def inicio(requisicao):
    receitas, busca, categoria, _ = receitas_filtradas(requisicao)
    return renderizar(
        requisicao,
        "index.html",
        {
            "receitas": receitas,
            "busca": busca,
            "categoria_ativa": categoria,
            "categorias": Receita.objects.values("categoria")
            .annotate(total=Contagem("id"))
            .order_by("categoria"),
        },
    )


def criar_conta(requisicao):
    if requisicao.method != "POST":
        return redirecionar("inicio")
    formulario = FormularioCadastro(requisicao.POST)
    if formulario.is_valid():
        usuario = formulario.salvar()
        iniciar_sessao(requisicao, usuario)
        mensagens.success(requisicao, "Conta criada com sucesso.")
        return redirecionar("minhas_receitas")
    mensagens.error(requisicao, "Não foi possível criar a conta. Verifique os dados.")
    return redirecionar(f"{reverter_url('inicio')}?autenticacao=cadastro")


def entrar(requisicao):
    if requisicao.method != "POST":
        return redirecionar("inicio")
    identificador = requisicao.POST.get(
        "identificador",
        requisicao.POST.get("email", ""),
    ).strip()
    senha = requisicao.POST.get("senha", "")
    usuario = autenticar(requisicao, username=identificador, password=senha)
    if usuario is None and identificador:
        usuarios_encontrados = list(
            Usuario.objects.filter(
                Ou(username__iexact=identificador) | Ou(email__iexact=identificador)
            ).distinct()[:2]
        )
        if len(usuarios_encontrados) == 1:
            usuario = autenticar(
                requisicao,
                username=usuarios_encontrados[0].username,
                password=senha,
            )
    if usuario is None:
        mensagens.error(requisicao, "E-mail, usuário ou senha inválidos.")
        return redirecionar(f"{reverter_url('inicio')}?autenticacao=entrar")

    iniciar_sessao(requisicao, usuario)
    mensagens.success(requisicao, "Login realizado com sucesso.")
    return redirecionar("painel_gestao" if usuario.is_superuser else "minhas_receitas")


@exige_login
def minhas_receitas(requisicao):
    if requisicao.user.is_superuser:
        return redirecionar("painel_gestao")
    receitas, busca, categoria, ordenacao = receitas_filtradas(requisicao)
    ids_receitas_favoritas = set(
        requisicao.user.receitas_favoritas.values_list("receita_id", flat=True)
    )
    return renderizar(
        requisicao,
        "painel_usuario.html",
        {
            "receitas": receitas,
            "ids_receitas_favoritas": ids_receitas_favoritas,
            "busca": busca,
            "categoria_ativa": categoria,
            "ordenacao": ordenacao,
            "categorias": Receita.objects.values("categoria")
            .annotate(total=Contagem("id"))
            .order_by("categoria"),
        },
    )


@exige_login
def alternar_favorito(requisicao, id_receita):
    if requisicao.method != "POST":
        return redirecionar("minhas_receitas")
    receita = obter_ou_404(Receita, id=id_receita)
    favorito, foi_criado = Favorito.objects.get_or_create(
        usuario=requisicao.user,
        receita=receita,
    )
    if not foi_criado:
        favorito.delete()
    proxima_url = requisicao.POST.get("proximo", "")
    if url_permitida(
        proxima_url,
        allowed_hosts={requisicao.get_host()},
        require_https=requisicao.is_secure(),
    ):
        return redirecionar(proxima_url)
    return redirecionar("minhas_receitas")


def detalhe_receita(requisicao, id_receita):
    receita = obter_ou_404(receitas_com_media_avaliacoes(), id=id_receita)
    esta_favoritada = requisicao.user.is_authenticated and Favorito.objects.filter(
        usuario=requisicao.user,
        receita=receita,
    ).exists()
    avaliacao_do_usuario = None
    if requisicao.user.is_authenticated:
        avaliacao_do_usuario = Avaliacao.objects.filter(
            usuario=requisicao.user,
            receita=receita,
        ).first()
    return renderizar(
        requisicao,
        "detalhe_receita.html",
        {
            "receita": receita,
            "esta_favoritada": esta_favoritada,
            "avaliacoes": receita.avaliacoes.select_related("usuario"),
            "avaliacao_do_usuario": avaliacao_do_usuario,
        },
    )


@exige_login
def avaliar_receita(requisicao, id_receita):
    if requisicao.method != "POST":
        return redirecionar("detalhe_receita", id_receita=id_receita)
    receita = obter_ou_404(Receita, id=id_receita)
    formulario = FormularioAvaliacaoReceita(requisicao.POST)
    if not formulario.is_valid():
        mensagens.error(requisicao, "Revise a nota e o comentário antes de publicar.")
        return redirecionar("detalhe_receita", id_receita=receita.id)
    Avaliacao.objects.update_or_create(
        usuario=requisicao.user,
        receita=receita,
        defaults={
            "nota": formulario.cleaned_data["nota"],
            "comentario": formulario.cleaned_data["comentario"].strip(),
        },
    )
    mensagens.success(requisicao, "Avaliação publicada.")
    return redirecionar("detalhe_receita", id_receita=receita.id)


@exige_login
def meu_perfil(requisicao):
    formulario = FormularioPerfil(requisicao.user, requisicao.POST or None)
    aba_ativa = requisicao.GET.get("aba", "perfil")
    if aba_ativa not in {"perfil", "favoritos"}:
        aba_ativa = "perfil"
    favoritos = Favorito.objects.filter(usuario=requisicao.user).select_related(
        "receita"
    )
    if requisicao.method == "POST" and formulario.is_valid():
        usuario = formulario.salvar()
        atualizar_hash_sessao(requisicao, usuario)
        mensagens.success(requisicao, "Perfil atualizado.")
        return redirecionar(
            "painel_gestao" if usuario.is_superuser else "minhas_receitas"
        )
    return renderizar(
        requisicao,
        "perfil.html",
        {
            "formulario": formulario,
            "aba_ativa": aba_ativa,
            "favoritos": favoritos,
            "nome_rota_voltar": (
                "painel_gestao"
                if requisicao.user.is_superuser
                else "minhas_receitas"
            ),
        },
    )


@exige_login
def sair(requisicao):
    if requisicao.method == "POST":
        encerrar_sessao(requisicao)
    return redirecionar("inicio")
