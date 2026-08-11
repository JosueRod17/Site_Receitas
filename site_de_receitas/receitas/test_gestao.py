from django.contrib.auth.models import Group as Grupo
from django.contrib.auth.models import User as Usuario
from django.test import TestCase as CasoDeTeste
from django.urls import reverse as reverter_url

from .modelos import Avaliacao, Favorito, Membro, Receita


class TestesAcessoGestao(CasoDeTeste):
    def setUp(self):
        self.superusuario = Usuario.objects.create_superuser(
            username="administrador",
            email="administrador@exemplo.com",
            password="senha-segura-123",
        )
        self.membro = Usuario.objects.create_user(
            username="membro",
            email="membro@exemplo.com",
            password="senha-segura-123",
        )
        self.cliente = self.client

    def test_gestao_exige_superusuario(self):
        resposta = self.cliente.get(reverter_url("painel_gestao"))
        self.assertRedirects(
            resposta,
            f"{reverter_url('inicio')}?autenticacao=entrar",
            fetch_redirect_response=False,
        )

        self.cliente.force_login(self.membro)
        resposta = self.cliente.get(reverter_url("painel_gestao"))
        self.assertEqual(resposta.status_code, 403)

    def test_criacao_de_membro_na_gestao_nao_e_publica(self):
        resposta = self.cliente.get(reverter_url("criar_membro_gestao"))
        self.assertRedirects(
            resposta,
            f"{reverter_url('inicio')}?autenticacao=entrar",
            fetch_redirect_response=False,
        )


class TestesCrudGestao(CasoDeTeste):
    def setUp(self):
        self.superusuario = Usuario.objects.create_superuser(
            username="administrador",
            email="administrador@exemplo.com",
            password="senha-segura-123",
        )
        self.membro = Usuario.objects.create_user(
            username="membro",
            email="membro@exemplo.com",
            password="senha-segura-123",
        )
        self.cliente = self.client
        self.cliente.force_login(self.superusuario)

    def test_superusuario_ve_painel_e_todas_as_secoes_de_gestao(self):
        nomes_das_rotas = [
            "painel_gestao",
            "gestao_receitas",
            "gestao_avaliacoes",
            "gestao_favoritos",
            "gestao_membros",
            "gestao_usuarios",
            "gestao_grupos",
        ]

        for nome_rota in nomes_das_rotas:
            with self.subTest(nome_rota=nome_rota):
                resposta = self.cliente.get(reverter_url(nome_rota))
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, "Painel de gestão")

    def test_receita_avaliacao_e_favorito_podem_ser_gerenciados(self):
        resposta = self.cliente.post(
            reverter_url("criar_receita_gestao"),
            {
                "titulo": "Receita administrativa",
                "categoria": "Teste",
                "url_imagem": "https://example.com/receita.jpg",
                "tempo_preparo": 25,
                "dificuldade": "Fácil",
                "descricao": "Descrição",
                "ingredientes": "Ingrediente",
                "modo_preparo": "Passo",
                "em_destaque": "on",
            },
        )
        self.assertRedirects(resposta, reverter_url("gestao_receitas"))
        receita = Receita.objects.get(titulo="Receita administrativa")

        resposta = self.cliente.post(
            reverter_url("criar_avaliacao_gestao"),
            {
                "receita": receita.pk,
                "usuario": self.membro.pk,
                "nota": 5,
                "comentario": "Ótima",
            },
        )
        self.assertRedirects(resposta, reverter_url("gestao_avaliacoes"))
        avaliacao = Avaliacao.objects.get(receita=receita, usuario=self.membro)

        resposta = self.cliente.post(
            reverter_url("criar_favorito_gestao"),
            {"receita": receita.pk, "usuario": self.membro.pk},
        )
        self.assertRedirects(resposta, reverter_url("gestao_favoritos"))
        favorito = Favorito.objects.get(receita=receita, usuario=self.membro)

        resposta = self.cliente.post(
            reverter_url("excluir_avaliacao_gestao", args=[avaliacao.pk])
        )
        self.assertRedirects(resposta, reverter_url("gestao_avaliacoes"))
        self.assertFalse(Avaliacao.objects.filter(pk=avaliacao.pk).exists())

        resposta = self.cliente.post(
            reverter_url("excluir_favorito_gestao", args=[favorito.pk])
        )
        self.assertRedirects(resposta, reverter_url("gestao_favoritos"))
        self.assertFalse(Favorito.objects.filter(pk=favorito.pk).exists())

    def test_membros_usuarios_e_grupos_podem_ser_gerenciados(self):
        resposta = self.cliente.post(
            reverter_url("criar_membro_gestao"),
            {
                "primeiro_nome": "Maria",
                "sobrenome": "Silva",
                "telefone": "11999999999",
                "data_ingresso": "2026-08-10",
            },
        )
        self.assertRedirects(resposta, reverter_url("gestao_membros"))
        self.assertTrue(
            Membro.objects.filter(
                primeiro_nome="Maria",
                sobrenome="Silva",
            ).exists()
        )

        resposta = self.cliente.post(
            reverter_url("criar_usuario_gestao"),
            {
                "username": "editor",
                "email": "editor@example.com",
                "first_name": "Editor",
                "last_name": "",
                "senha": "senha-segura-123",
                "is_active": "on",
            },
        )
        self.assertRedirects(resposta, reverter_url("gestao_usuarios"))
        editor = Usuario.objects.get(username="editor")
        self.assertTrue(editor.check_password("senha-segura-123"))

        resposta = self.cliente.post(
            reverter_url("criar_grupo_gestao"),
            {"name": "Editores"},
        )
        self.assertRedirects(resposta, reverter_url("gestao_grupos"))
        self.assertTrue(Grupo.objects.filter(name="Editores").exists())

    def test_superusuario_nao_pode_excluir_propria_conta(self):
        resposta = self.cliente.post(
            reverter_url("excluir_usuario_gestao", args=[self.superusuario.pk])
        )

        self.assertRedirects(resposta, reverter_url("gestao_usuarios"))
        self.assertTrue(Usuario.objects.filter(pk=self.superusuario.pk).exists())

    def test_edicao_da_propria_senha_mantem_sessao_da_gestao_ativa(self):
        resposta = self.cliente.post(
            reverter_url("editar_usuario_gestao", args=[self.superusuario.pk]),
            {
                "username": "administrador",
                "email": "administrador@exemplo.com",
                "first_name": "",
                "last_name": "",
                "senha": "outra-senha-segura-123",
                "is_active": "on",
                "is_staff": "on",
                "is_superuser": "on",
            },
        )

        self.assertRedirects(resposta, reverter_url("gestao_usuarios"))
        self.superusuario.refresh_from_db()
        self.assertTrue(self.superusuario.check_password("outra-senha-segura-123"))
        self.assertEqual(
            self.cliente.get(reverter_url("painel_gestao")).status_code,
            200,
        )
