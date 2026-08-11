from django.contrib import messages as mensagens
from django.contrib.auth import update_session_auth_hash as atualizar_hash_sessao
from django.contrib.auth.models import Group as Grupo
from django.contrib.auth.models import User as Usuario
from django.core.paginator import Paginator as Paginador
from django.db.models import Avg as Media
from django.db.models import Count as Contagem
from django.db.models import Q as Ou
from django.shortcuts import get_object_or_404 as obter_ou_404
from django.shortcuts import redirect as redirecionar
from django.shortcuts import render as renderizar
from django.views.decorators.http import require_POST as exige_post

from .controle_acesso import exige_superusuario
from .formularios_gestao import (
    FormularioGestaoAvaliacao,
    FormularioGestaoFavorito,
    FormularioGestaoGrupo,
    FormularioGestaoMembro,
    FormularioGestaoReceita,
    FormularioGestaoUsuario,
)
from .modelos import Avaliacao, Favorito, Membro, Receita


def _obter_pagina(requisicao, consulta, itens_por_pagina=16):
    return Paginador(consulta, itens_por_pagina).get_page(requisicao.GET.get("pagina"))


def _obter_busca(requisicao):
    return requisicao.GET.get("busca", "").strip()


def _resposta_lista(requisicao, *, secao, titulo_pagina, consulta, busca):
    return renderizar(
        requisicao,
        "gestao/lista_registros.html",
        {
            "secao": secao,
            "titulo_pagina": titulo_pagina,
            "pagina_objetos": _obter_pagina(requisicao, consulta),
            "busca": busca,
        },
    )


def _resposta_formulario(
    requisicao,
    *,
    secao,
    titulo_pagina,
    classe_formulario,
    nome_rota_lista,
    instancia=None,
    autor=None,
):
    argumentos_formulario = {"instance": instancia} if instancia is not None else {}
    if classe_formulario is FormularioGestaoUsuario:
        argumentos_formulario["autor"] = autor
    formulario = classe_formulario(requisicao.POST or None, **argumentos_formulario)
    if requisicao.method == "POST" and formulario.is_valid():
        objeto_salvo = formulario.save()
        if (
            classe_formulario is FormularioGestaoUsuario
            and objeto_salvo.pk == requisicao.user.pk
        ):
            atualizar_hash_sessao(requisicao, objeto_salvo)
        mensagens.success(requisicao, "Alterações salvas com sucesso.")
        return redirecionar(nome_rota_lista)
    return renderizar(
        requisicao,
        "gestao/formulario_registro.html",
        {
            "secao": secao,
            "titulo_pagina": titulo_pagina,
            "formulario": formulario,
            "nome_rota_cancelar": nome_rota_lista,
        },
    )


@exige_superusuario
def painel_gestao(requisicao):
    receitas_em_destaque = (
        Receita.objects.annotate(
            media_avaliacoes=Media("avaliacoes__nota"),
            total_avaliacoes=Contagem("avaliacoes"),
        )
        .order_by("-total_avaliacoes", "-media_avaliacoes", "titulo")[:6]
    )
    avaliacoes_recentes = Avaliacao.objects.select_related("receita", "usuario")[:6]
    estatisticas = [
        {"rotulo": "Receitas", "valor": Receita.objects.count(), "rota": "gestao_receitas"},
        {
            "rotulo": "Avaliações",
            "valor": Avaliacao.objects.count(),
            "rota": "gestao_avaliacoes",
        },
        {
            "rotulo": "Favoritos",
            "valor": Favorito.objects.count(),
            "rota": "gestao_favoritos",
        },
        {"rotulo": "Membros", "valor": Membro.objects.count(), "rota": "gestao_membros"},
        {"rotulo": "Usuários", "valor": Usuario.objects.count(), "rota": "gestao_usuarios"},
        {"rotulo": "Grupos", "valor": Grupo.objects.count(), "rota": "gestao_grupos"},
    ]
    return renderizar(
        requisicao,
        "gestao/painel.html",
        {
            "titulo_pagina": "Visão geral",
            "secao": "painel",
            "estatisticas": estatisticas,
            "receitas_em_destaque": receitas_em_destaque,
            "avaliacoes_recentes": avaliacoes_recentes,
        },
    )


@exige_superusuario
def listar_receitas_gestao(requisicao):
    busca = _obter_busca(requisicao)
    consulta = Receita.objects.annotate(
        media_avaliacoes=Media("avaliacoes__nota"),
        total_avaliacoes=Contagem("avaliacoes"),
    )
    if busca:
        consulta = consulta.filter(
            Ou(titulo__icontains=busca) | Ou(categoria__icontains=busca)
        )
    return _resposta_lista(
        requisicao,
        secao="receitas",
        titulo_pagina="Receitas",
        consulta=consulta.order_by("-criada_em", "titulo"),
        busca=busca,
    )


@exige_superusuario
def criar_receita_gestao(requisicao):
    return _resposta_formulario(
        requisicao,
        secao="receitas",
        titulo_pagina="Nova receita",
        classe_formulario=FormularioGestaoReceita,
        nome_rota_lista="gestao_receitas",
    )


@exige_superusuario
def editar_receita_gestao(requisicao, id_receita):
    return _resposta_formulario(
        requisicao,
        secao="receitas",
        titulo_pagina="Editar receita",
        classe_formulario=FormularioGestaoReceita,
        nome_rota_lista="gestao_receitas",
        instancia=obter_ou_404(Receita, pk=id_receita),
    )


@exige_post
@exige_superusuario
def excluir_receita_gestao(requisicao, id_receita):
    obter_ou_404(Receita, pk=id_receita).delete()
    mensagens.success(requisicao, "Receita removida.")
    return redirecionar("gestao_receitas")


@exige_superusuario
def listar_avaliacoes_gestao(requisicao):
    busca = _obter_busca(requisicao)
    consulta = Avaliacao.objects.select_related("receita", "usuario")
    if busca:
        consulta = consulta.filter(
            Ou(receita__titulo__icontains=busca)
            | Ou(usuario__username__icontains=busca)
            | Ou(usuario__email__icontains=busca)
            | Ou(comentario__icontains=busca)
        )
    return _resposta_lista(
        requisicao,
        secao="avaliacoes",
        titulo_pagina="Avaliações",
        consulta=consulta,
        busca=busca,
    )


@exige_superusuario
def criar_avaliacao_gestao(requisicao):
    return _resposta_formulario(
        requisicao,
        secao="avaliacoes",
        titulo_pagina="Nova avaliação",
        classe_formulario=FormularioGestaoAvaliacao,
        nome_rota_lista="gestao_avaliacoes",
    )


@exige_superusuario
def editar_avaliacao_gestao(requisicao, id_avaliacao):
    return _resposta_formulario(
        requisicao,
        secao="avaliacoes",
        titulo_pagina="Editar avaliação",
        classe_formulario=FormularioGestaoAvaliacao,
        nome_rota_lista="gestao_avaliacoes",
        instancia=obter_ou_404(Avaliacao, pk=id_avaliacao),
    )


@exige_post
@exige_superusuario
def excluir_avaliacao_gestao(requisicao, id_avaliacao):
    obter_ou_404(Avaliacao, pk=id_avaliacao).delete()
    mensagens.success(requisicao, "Avaliação removida.")
    return redirecionar("gestao_avaliacoes")


@exige_superusuario
def listar_favoritos_gestao(requisicao):
    busca = _obter_busca(requisicao)
    consulta = Favorito.objects.select_related("receita", "usuario")
    if busca:
        consulta = consulta.filter(
            Ou(receita__titulo__icontains=busca)
            | Ou(usuario__username__icontains=busca)
            | Ou(usuario__email__icontains=busca)
        )
    return _resposta_lista(
        requisicao,
        secao="favoritos",
        titulo_pagina="Favoritos",
        consulta=consulta.order_by("-criado_em"),
        busca=busca,
    )


@exige_superusuario
def criar_favorito_gestao(requisicao):
    return _resposta_formulario(
        requisicao,
        secao="favoritos",
        titulo_pagina="Novo favorito",
        classe_formulario=FormularioGestaoFavorito,
        nome_rota_lista="gestao_favoritos",
    )


@exige_superusuario
def editar_favorito_gestao(requisicao, id_favorito):
    return _resposta_formulario(
        requisicao,
        secao="favoritos",
        titulo_pagina="Editar favorito",
        classe_formulario=FormularioGestaoFavorito,
        nome_rota_lista="gestao_favoritos",
        instancia=obter_ou_404(Favorito, pk=id_favorito),
    )


@exige_post
@exige_superusuario
def excluir_favorito_gestao(requisicao, id_favorito):
    obter_ou_404(Favorito, pk=id_favorito).delete()
    mensagens.success(requisicao, "Favorito removido.")
    return redirecionar("gestao_favoritos")


@exige_superusuario
def listar_membros_gestao(requisicao):
    busca = _obter_busca(requisicao)
    consulta = Membro.objects.all()
    if busca:
        filtros = Ou(primeiro_nome__icontains=busca) | Ou(sobrenome__icontains=busca)
        if busca.isdigit():
            filtros |= Ou(telefone=int(busca))
        consulta = consulta.filter(filtros)
    return _resposta_lista(
        requisicao,
        secao="membros",
        titulo_pagina="Membros",
        consulta=consulta.order_by("primeiro_nome", "sobrenome"),
        busca=busca,
    )


@exige_superusuario
def criar_membro_gestao(requisicao):
    return _resposta_formulario(
        requisicao,
        secao="membros",
        titulo_pagina="Novo membro",
        classe_formulario=FormularioGestaoMembro,
        nome_rota_lista="gestao_membros",
    )


@exige_superusuario
def editar_membro_gestao(requisicao, id_membro):
    return _resposta_formulario(
        requisicao,
        secao="membros",
        titulo_pagina="Editar membro",
        classe_formulario=FormularioGestaoMembro,
        nome_rota_lista="gestao_membros",
        instancia=obter_ou_404(Membro, pk=id_membro),
    )


@exige_post
@exige_superusuario
def excluir_membro_gestao(requisicao, id_membro):
    obter_ou_404(Membro, pk=id_membro).delete()
    mensagens.success(requisicao, "Membro removido.")
    return redirecionar("gestao_membros")


@exige_superusuario
def listar_usuarios_gestao(requisicao):
    busca = _obter_busca(requisicao)
    consulta = Usuario.objects.prefetch_related("groups")
    if busca:
        consulta = consulta.filter(
            Ou(username__icontains=busca)
            | Ou(email__icontains=busca)
            | Ou(first_name__icontains=busca)
            | Ou(last_name__icontains=busca)
        )
    return _resposta_lista(
        requisicao,
        secao="usuarios",
        titulo_pagina="Usuários",
        consulta=consulta.order_by("username"),
        busca=busca,
    )


@exige_superusuario
def criar_usuario_gestao(requisicao):
    return _resposta_formulario(
        requisicao,
        secao="usuarios",
        titulo_pagina="Novo usuário",
        classe_formulario=FormularioGestaoUsuario,
        nome_rota_lista="gestao_usuarios",
        autor=requisicao.user,
    )


@exige_superusuario
def editar_usuario_gestao(requisicao, id_usuario):
    return _resposta_formulario(
        requisicao,
        secao="usuarios",
        titulo_pagina="Editar usuário",
        classe_formulario=FormularioGestaoUsuario,
        nome_rota_lista="gestao_usuarios",
        instancia=obter_ou_404(Usuario, pk=id_usuario),
        autor=requisicao.user,
    )


@exige_post
@exige_superusuario
def excluir_usuario_gestao(requisicao, id_usuario):
    usuario = obter_ou_404(Usuario, pk=id_usuario)
    if usuario.pk == requisicao.user.pk:
        mensagens.error(requisicao, "Você não pode excluir sua própria conta administrativa.")
    else:
        usuario.delete()
        mensagens.success(requisicao, "Usuário removido.")
    return redirecionar("gestao_usuarios")


@exige_superusuario
def listar_grupos_gestao(requisicao):
    busca = _obter_busca(requisicao)
    consulta = Grupo.objects.annotate(
        total_membros=Contagem("user", distinct=True),
        total_permissoes=Contagem("permissions", distinct=True),
    )
    if busca:
        consulta = consulta.filter(name__icontains=busca)
    return _resposta_lista(
        requisicao,
        secao="grupos",
        titulo_pagina="Grupos e permissões",
        consulta=consulta.order_by("name"),
        busca=busca,
    )


@exige_superusuario
def criar_grupo_gestao(requisicao):
    return _resposta_formulario(
        requisicao,
        secao="grupos",
        titulo_pagina="Novo grupo",
        classe_formulario=FormularioGestaoGrupo,
        nome_rota_lista="gestao_grupos",
    )


@exige_superusuario
def editar_grupo_gestao(requisicao, id_grupo):
    return _resposta_formulario(
        requisicao,
        secao="grupos",
        titulo_pagina="Editar grupo",
        classe_formulario=FormularioGestaoGrupo,
        nome_rota_lista="gestao_grupos",
        instancia=obter_ou_404(Grupo, pk=id_grupo),
    )


@exige_post
@exige_superusuario
def excluir_grupo_gestao(requisicao, id_grupo):
    obter_ou_404(Grupo, pk=id_grupo).delete()
    mensagens.success(requisicao, "Grupo removido.")
    return redirecionar("gestao_grupos")
