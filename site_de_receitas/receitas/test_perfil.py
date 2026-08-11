from django.contrib.auth.models import User as Usuario
from django.test import TestCase as CasoDeTeste

from .formularios import FormularioPerfil


class TestesFormularioPerfil(CasoDeTeste):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="ana@example.com",
            email="ana@example.com",
            first_name="Ana",
            password="senha-segura-123",
        )

    def dados_do_formulario(self, **substituicoes):
        dados = {
            "apelido": "Ana",
            "email": "ana@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmacao_nova_senha": "",
        }
        dados.update(substituicoes)
        return dados

    def test_exibe_email_atual_como_valor_inicial(self):
        formulario = FormularioPerfil(self.usuario)

        self.assertEqual(formulario["email"].value(), "ana@example.com")

    def test_salva_novo_email_e_atualiza_nome_de_usuario_correspondente(self):
        formulario = FormularioPerfil(
            self.usuario,
            self.dados_do_formulario(
                apelido="Ana Silva",
                email="ana.silva@example.com",
                senha_atual="senha-segura-123",
            ),
        )

        self.assertTrue(formulario.is_valid())
        usuario = formulario.salvar()

        self.assertEqual(usuario.first_name, "Ana Silva")
        self.assertEqual(usuario.email, "ana.silva@example.com")
        self.assertEqual(usuario.username, "ana.silva@example.com")

    def test_mantem_nome_de_usuario_independente_quando_email_muda(self):
        administrador = Usuario.objects.create_superuser(
            username="administrador",
            email="administrador@example.com",
            password="senha-segura-123",
        )
        formulario = FormularioPerfil(
            administrador,
            self.dados_do_formulario(
                apelido="Admin",
                email="novo-administrador@example.com",
                senha_atual="senha-segura-123",
            ),
        )

        self.assertTrue(formulario.is_valid())
        usuario = formulario.salvar()

        self.assertEqual(usuario.username, "administrador")
        self.assertEqual(usuario.email, "novo-administrador@example.com")

    def test_rejeita_email_ja_usado_por_outra_conta(self):
        Usuario.objects.create_user(
            username="bia@example.com",
            email="bia@example.com",
            password="senha-segura-123",
        )
        formulario = FormularioPerfil(
            self.usuario,
            self.dados_do_formulario(email="BIA@EXAMPLE.COM"),
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

    def test_exige_senha_atual_para_alterar_email(self):
        formulario = FormularioPerfil(
            self.usuario,
            self.dados_do_formulario(email="novo-email@example.com"),
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("senha_atual", formulario.errors)

    def test_permite_alterar_apelido_sem_senha_atual(self):
        formulario = FormularioPerfil(
            self.usuario,
            self.dados_do_formulario(apelido="Ana Maria"),
        )

        self.assertTrue(formulario.is_valid())

    def test_rejeita_email_que_e_nome_de_usuario_de_outra_pessoa(self):
        Usuario.objects.create_user(
            username="reservado@example.com",
            email="outro@example.com",
            password="senha-segura-123",
        )
        formulario = FormularioPerfil(
            self.usuario,
            self.dados_do_formulario(email="reservado@example.com"),
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

    def test_valida_nova_senha_com_email_e_apelido_novos(self):
        formulario = FormularioPerfil(
            self.usuario,
            self.dados_do_formulario(
                apelido="Ana Cozinha",
                email="cozinha@example.com",
                senha_atual="senha-segura-123",
                nova_senha="cozinha@example.com",
                confirmacao_nova_senha="cozinha@example.com",
            ),
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("nova_senha", formulario.errors)
