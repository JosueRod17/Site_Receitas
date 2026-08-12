from django.contrib.auth.models import User as Usuario
from django.test import TestCase as CasoDeTeste
from django.urls import reverse as reverter_url

from .modelos import Avaliacao, Favorito, Receita
from .visoes import receitas_com_media_avaliacoes


class TestesFluxoDeAutenticacao(CasoDeTeste):
    def setUp(self):
        self.membro = Usuario.objects.create_user(
            username="membro-login",
            email="membro@exemplo.com",
            first_name="Membro",
            password="senha-segura-123",
        )
        self.superusuario = Usuario.objects.create_superuser(
            username="administrador",
            email="administrador@exemplo.com",
            password="senha-segura-123",
        )
        self.cliente = self.client

    def test_membro_pode_entrar_com_email_quando_nome_de_usuario_e_diferente(self):
        resposta = self.cliente.post(
            reverter_url("entrar"),
            {"identificador": "membro@exemplo.com", "senha": "senha-segura-123"},
        )

        self.assertRedirects(resposta, reverter_url("minhas_receitas"))
        self.assertEqual(
            self.cliente.session["_auth_user_id"],
            str(self.membro.pk),
        )

    def test_superusuario_pode_entrar_com_nome_de_usuario_e_acessa_gestao(self):
        resposta = self.cliente.post(
            reverter_url("entrar"),
            {"identificador": "administrador", "senha": "senha-segura-123"},
        )

        self.assertRedirects(resposta, reverter_url("painel_gestao"))
        self.assertEqual(
            self.cliente.session["_auth_user_id"],
            str(self.superusuario.pk),
        )

    def test_perfil_exibe_e_atualiza_email(self):
        self.cliente.force_login(self.membro)

        resposta = self.cliente.get(reverter_url("meu_perfil"))
        self.assertContains(resposta, "membro@exemplo.com")

        resposta = self.cliente.post(
            reverter_url("meu_perfil"),
            {
                "apelido": "Novo nome",
                "nome_usuario": "membro-login",
                "email": "novo@exemplo.com",
                "senha_atual": "senha-segura-123",
                "nova_senha": "",
                "confirmacao_nova_senha": "",
            },
        )

        self.assertRedirects(resposta, reverter_url("minhas_receitas"))
        self.membro.refresh_from_db()
        self.assertEqual(self.membro.email, "novo@exemplo.com")

    def test_email_sem_senha_atual_mantem_confirmacao_visivel_no_perfil(self):
        self.cliente.force_login(self.membro)

        resposta = self.cliente.post(
            reverter_url("meu_perfil"),
            {
                "apelido": "Membro",
                "nome_usuario": "membro-login",
                "email": "novo@exemplo.com",
                "senha_atual": "",
                "nova_senha": "",
                "confirmacao_nova_senha": "",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'data-senha-atual-visivel="true"')
        self.assertContains(resposta, "Informe sua senha atual")

    def test_perfil_exibe_favoritos_em_aba_propria(self):
        receita = Receita.objects.create(
            titulo="Receita favorita",
            categoria="Teste",
            url_imagem="https://example.com/receita.jpg",
            tempo_preparo=15,
            dificuldade="Fácil",
        )
        Favorito.objects.create(usuario=self.membro, receita=receita)
        self.cliente.force_login(self.membro)

        resposta = self.cliente.get(f"{reverter_url('meu_perfil')}?aba=favoritos")

        self.assertContains(resposta, "Minhas favoritas")
        self.assertContains(resposta, "Receita favorita")
        self.assertContains(resposta, "Remover")


class TestesDeAvaliacoes(CasoDeTeste):
    def setUp(self):
        self.autor = Usuario.objects.create_user(
            username="autor",
            email="autor@exemplo.com",
            password="senha-segura-123",
        )
        self.receita = Receita.objects.create(
            titulo="Receita sem avaliação",
            categoria="Teste",
            url_imagem="https://example.com/receita.jpg",
            tempo_preparo=20,
            dificuldade="Fácil",
            nota=4.5,
        )
        self.cliente = self.client

    def test_receita_sem_avaliacoes_nao_tem_nota_publica(self):
        receita = receitas_com_media_avaliacoes().get(pk=self.receita.pk)

        self.assertIsNone(receita.media_avaliacoes)
        self.assertEqual(receita.total_avaliacoes, 0)

        resposta = self.cliente.get(reverter_url("inicio"))
        self.assertContains(resposta, "Sem avaliações")
        self.assertNotContains(resposta, 'class="tag"')

    def test_media_e_total_sao_calculados_pelas_avaliacoes(self):
        segundo_usuario = Usuario.objects.create_user(
            username="segundo",
            email="segundo@exemplo.com",
            password="senha-segura-123",
        )
        Avaliacao.objects.create(usuario=self.autor, receita=self.receita, nota=3)
        Avaliacao.objects.create(
            usuario=segundo_usuario,
            receita=self.receita,
            nota=5,
        )

        receita = receitas_com_media_avaliacoes().get(pk=self.receita.pk)

        self.assertEqual(receita.media_avaliacoes, 4)
        self.assertEqual(receita.total_avaliacoes, 2)
        resposta = self.cliente.get(
            reverter_url("detalhe_receita", args=[self.receita.pk])
        )
        self.assertContains(resposta, "4,0/5")
        self.assertContains(resposta, "2 avaliações")

    def test_avaliacao_rejeita_comentario_maior_que_limite_permitido(self):
        self.cliente.force_login(self.autor)

        resposta = self.cliente.post(
            reverter_url("avaliar_receita", args=[self.receita.pk]),
            {"nota": 5, "comentario": "x" * 1001},
            follow=True,
        )

        self.assertFalse(
            Avaliacao.objects.filter(
                usuario=self.autor,
                receita=self.receita,
            ).exists()
        )
        self.assertContains(resposta, "Revise a nota e o comentário antes de publicar.")

    def test_favorito_nao_redireciona_para_url_externa_enviada(self):
        self.cliente.force_login(self.autor)

        resposta = self.cliente.post(
            reverter_url("alternar_favorito", args=[self.receita.pk]),
            {"proximo": "https://example.org/nao-confiavel"},
        )

        self.assertRedirects(resposta, reverter_url("minhas_receitas"))
