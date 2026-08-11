from django import forms
from django.contrib.auth.models import Group as Grupo
from django.contrib.auth.models import User as Usuario
from django.contrib.auth.password_validation import validate_password as validar_senha
from django.db.models import Q

from .modelos import Avaliacao, Favorito, Membro, Receita


class FormularioGestaoReceita(forms.ModelForm):
    """Campos editáveis da receita na área de gestão.

    A nota pública é calculada pelas avaliações reais e não é editada aqui.
    """

    class Meta:
        model = Receita
        fields = [
            "titulo",
            "categoria",
            "url_imagem",
            "tempo_preparo",
            "dificuldade",
            "descricao",
            "ingredientes",
            "modo_preparo",
            "em_destaque",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "ingredientes": forms.Textarea(attrs={"rows": 7}),
            "modo_preparo": forms.Textarea(attrs={"rows": 7}),
            "url_imagem": forms.URLInput(attrs={"placeholder": "https://..."}),
            "tempo_preparo": forms.NumberInput(attrs={"min": 1}),
        }


class FormularioGestaoMembro(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ["primeiro_nome", "sobrenome", "telefone", "data_ingresso"]
        widgets = {
            "telefone": forms.NumberInput(attrs={"min": 0}),
            "data_ingresso": forms.DateInput(attrs={"type": "date"}),
        }


class FormularioGestaoAvaliacao(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ["receita", "usuario", "nota", "comentario"]
        widgets = {
            "nota": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comentario": forms.Textarea(attrs={"rows": 5}),
        }


class FormularioGestaoFavorito(forms.ModelForm):
    class Meta:
        model = Favorito
        fields = ["usuario", "receita"]


class FormularioGestaoUsuario(forms.ModelForm):
    senha = forms.CharField(
        label="Nova senha",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Obrigatória para uma nova conta. Deixe em branco para manter a senha atual.",
    )
    email = forms.EmailField(required=False)

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        ]
        widgets = {
            "groups": forms.CheckboxSelectMultiple,
            "user_permissions": forms.CheckboxSelectMultiple,
        }
        labels = {
            "username": "Nome de usuário",
            "email": "E-mail",
            "first_name": "Primeiro nome",
            "last_name": "Sobrenome",
            "is_active": "Conta ativa",
            "is_staff": "Acesso à equipe",
            "is_superuser": "Superusuário",
            "groups": "Grupos",
            "user_permissions": "Permissões específicas",
        }

    def __init__(self, *argumentos, autor=None, **argumentos_nomeados):
        super().__init__(*argumentos, **argumentos_nomeados)
        self.autor = autor
        self.nome_usuario_original = self.instance.username
        self.email_original = self.instance.email

    def clean_username(self):
        nome_usuario = self.cleaned_data["username"].strip()
        if Usuario.objects.filter(username__iexact=nome_usuario).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        if Usuario.objects.filter(email__iexact=nome_usuario).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError(
                "Este nome de usuário já está sendo usado como e-mail."
            )
        return nome_usuario

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not email:
            return email
        if Usuario.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        dados_limpos = super().clean()
        if not self.instance.pk and not dados_limpos.get("senha"):
            self.add_error("senha", "Informe uma senha para a nova conta.")
        if dados_limpos.get("senha"):
            usuario_candidato = Usuario(
                username=dados_limpos.get("username", self.instance.username),
                email=dados_limpos.get("email", self.instance.email),
                first_name=dados_limpos.get("first_name", self.instance.first_name),
                last_name=dados_limpos.get("last_name", self.instance.last_name),
            )
            try:
                validar_senha(dados_limpos["senha"], usuario_candidato)
            except forms.ValidationError as erro:
                self.add_error("senha", erro)
        if self.autor and self.instance.pk == self.autor.pk:
            campos_protegidos = ("is_active", "is_staff", "is_superuser")
            if any(not dados_limpos.get(campo) for campo in campos_protegidos):
                raise forms.ValidationError(
                    "Você não pode remover seu próprio acesso administrativo por este painel."
                )
        return dados_limpos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if (
            self.nome_usuario_original.casefold() == self.email_original.casefold()
            and self.cleaned_data["username"].casefold()
            == self.nome_usuario_original.casefold()
        ):
            usuario.username = usuario.email
        if self.cleaned_data.get("senha"):
            usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario


class FormularioGestaoGrupo(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ["name", "permissions"]
        widgets = {"permissions": forms.CheckboxSelectMultiple}
        labels = {"name": "Nome", "permissions": "Permissões"}

    def clean_name(self):
        nome = self.cleaned_data["name"].strip()
        if Grupo.objects.filter(name__iexact=nome).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Já existe um grupo com este nome.")
        return nome
