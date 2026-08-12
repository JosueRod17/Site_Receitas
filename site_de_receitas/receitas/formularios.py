from django import forms
from django.contrib.auth.models import User as Usuario
from django.contrib.auth.password_validation import validate_password as validar_senha
from django.db.models import Q

from .modelos import Membro


class FormularioMembro(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ["primeiro_nome", "sobrenome", "telefone", "data_ingresso"]
        widgets = {
            "data_ingresso": forms.DateInput(attrs={"type": "date"}),
            "telefone": forms.NumberInput(attrs={"placeholder": "Digite apenas números"}),
        }
        labels = {
            "primeiro_nome": "Primeiro nome",
            "sobrenome": "Sobrenome",
            "telefone": "Telefone",
            "data_ingresso": "Data de ingresso",
        }


class FormularioCadastro(forms.Form):
    apelido = forms.CharField(max_length=30)
    email = forms.EmailField()
    senha1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    senha2 = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if Usuario.objects.filter(
            Q(username__iexact=email) | Q(email__iexact=email)
        ).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        dados_limpos = super().clean()
        if dados_limpos.get("senha1") != dados_limpos.get("senha2"):
            self.add_error("senha2", "As senhas não coincidem.")
        elif dados_limpos.get("senha1"):
            usuario_candidato = Usuario(
                username=dados_limpos.get("email", ""),
                email=dados_limpos.get("email", ""),
                first_name=dados_limpos.get("apelido", ""),
            )
            try:
                validar_senha(dados_limpos["senha1"], usuario_candidato)
            except forms.ValidationError as erro:
                self.add_error("senha1", erro)
        return dados_limpos

    def salvar(self):
        return Usuario.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["apelido"],
            password=self.cleaned_data["senha1"],
        )


class FormularioAvaliacaoReceita(forms.Form):
    nota = forms.IntegerField(min_value=1, max_value=5)
    comentario = forms.CharField(required=False, max_length=1000)


class FormularioPerfil(forms.Form):
    apelido = forms.CharField(max_length=30)
    nome_usuario = forms.CharField(max_length=150)
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    senha_atual = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    nova_senha = forms.CharField(
        required=False,
        min_length=8,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirmacao_nova_senha = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, usuario, *argumentos, **argumentos_nomeados):
        super().__init__(*argumentos, **argumentos_nomeados)
        self.usuario = usuario
        self.fields["apelido"].initial = usuario.first_name
        self.fields["nome_usuario"].initial = usuario.username
        self.fields["email"].initial = usuario.email

    def clean_nome_usuario(self):
        nome_usuario = self.cleaned_data["nome_usuario"].strip()
        if Usuario.objects.filter(
            Q(username__iexact=nome_usuario) | Q(email__iexact=nome_usuario)
        ).exclude(pk=self.usuario.pk).exists():
            raise forms.ValidationError(
                "Este nome de usuário já está sendo usado por outra conta."
            )
        return nome_usuario

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        email_em_uso = Usuario.objects.filter(
            Q(username__iexact=email) | Q(email__iexact=email)
        ).exclude(pk=self.usuario.pk)
        if email_em_uso.exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        dados = super().clean()
        nome_usuario = dados.get("nome_usuario", self.usuario.username)
        email = dados.get("email", self.usuario.email)
        senha_atual = dados.get("senha_atual")
        nova_senha = dados.get("nova_senha")
        confirmacao_nova_senha = dados.get("confirmacao_nova_senha")
        apelido = dados.get("apelido", self.usuario.first_name)
        apelido_alterado = apelido != self.usuario.first_name
        nome_usuario_alterado = nome_usuario.casefold() != self.usuario.username.casefold()
        email_alterado = email.casefold() != self.usuario.email.casefold()
        deseja_alterar_senha = bool(nova_senha or confirmacao_nova_senha)

        if (
            apelido_alterado
            or nome_usuario_alterado
            or email_alterado
            or deseja_alterar_senha
        ):
            if not senha_atual:
                self.add_error(
                    "senha_atual",
                    "Informe sua senha atual para confirmar esta alteração.",
                )
            elif not self.usuario.check_password(senha_atual):
                self.add_error("senha_atual", "A senha atual está incorreta.")

        if deseja_alterar_senha:
            if not nova_senha:
                self.add_error("nova_senha", "Informe a nova senha.")
            if not confirmacao_nova_senha:
                self.add_error("confirmacao_nova_senha", "Confirme a nova senha.")
            if senha_atual and nova_senha and confirmacao_nova_senha:
                if nova_senha != confirmacao_nova_senha:
                    self.add_error(
                        "confirmacao_nova_senha",
                        "As novas senhas não coincidem.",
                    )
                else:
                    nome_usuario_candidato = nome_usuario
                    if (
                        self.usuario.username.casefold()
                        == self.usuario.email.casefold()
                        and nome_usuario.casefold()
                        == self.usuario.username.casefold()
                    ):
                        nome_usuario_candidato = email
                    usuario_candidato = Usuario(
                        username=nome_usuario_candidato,
                        email=email,
                        first_name=dados.get("apelido", self.usuario.first_name),
                        last_name=self.usuario.last_name,
                    )
                    try:
                        validar_senha(nova_senha, usuario_candidato)
                    except forms.ValidationError as erro:
                        self.add_error("nova_senha", erro)
        return dados

    def salvar(self):
        self.usuario.first_name = self.cleaned_data["apelido"]
        nome_usuario = self.cleaned_data["nome_usuario"]
        if (
            self.usuario.username.casefold() == self.usuario.email.casefold()
            and nome_usuario.casefold() == self.usuario.username.casefold()
        ):
            self.usuario.username = self.cleaned_data["email"]
        else:
            self.usuario.username = nome_usuario
        self.usuario.email = self.cleaned_data["email"]
        if self.cleaned_data.get("nova_senha"):
            self.usuario.set_password(self.cleaned_data["nova_senha"])
        self.usuario.save()
        return self.usuario
