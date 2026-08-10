from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from .models import Membros


class MembrosForm(forms.ModelForm):
    class Meta:
        model = Membros
        fields = ['firstname', 'lastname', 'telefone', 'data_ingresso']  # noqa: RUF012
        widgets = {  # noqa: RUF012
            'data_ingresso': forms.DateInput(attrs={'type': 'date'}),
            'telefone': forms.NumberInput(attrs={'placeholder': 'Digite apenas números'})
        }
        labels = {  # noqa: RUF012
            'firstname': 'Primeiro Nome',
            'lastname': 'Último Nome',
            'telefone': 'Telefone',
            'data_ingresso': 'Data de Ingresso'
        }


class SignupForm(forms.Form):
    nickname = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "As senhas não coincidem.")
        elif cleaned_data.get("password1"):
            candidate = User(
                username=cleaned_data.get("email", ""),
                email=cleaned_data.get("email", ""),
                first_name=cleaned_data.get("nickname", ""),
            )
            try:
                validate_password(cleaned_data["password1"], candidate)
            except forms.ValidationError as error:
                self.add_error("password1", error)
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["nickname"],
            password=self.cleaned_data["password1"],
        )


class RecipeReviewForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(required=False, max_length=1000)


class ProfileForm(forms.Form):
    nickname = forms.CharField(max_length=30)
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    current_password = forms.CharField(required=False, widget=forms.PasswordInput)
    new_password1 = forms.CharField(required=False, min_length=8, widget=forms.PasswordInput)
    new_password2 = forms.CharField(required=False, widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["nickname"].initial = user.first_name
        self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        email_in_use = User.objects.filter(
            Q(username__iexact=email) | Q(email__iexact=email)
        ).exclude(pk=self.user.pk)
        if email_in_use.exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        data = super().clean()
        email = data.get("email", self.user.email)
        senha_atual = data.get("current_password")
        nova_senha = data.get("new_password1")
        confirmacao_nova_senha = data.get("new_password2")
        email_alterado = email.casefold() != self.user.email.casefold()
        deseja_alterar_senha = bool(nova_senha or confirmacao_nova_senha)

        if email_alterado or deseja_alterar_senha:
            if not senha_atual:
                self.add_error(
                    "current_password",
                    "Informe sua senha atual para confirmar esta alteração.",
                )
            elif not self.user.check_password(senha_atual):
                self.add_error("current_password", "A senha atual está incorreta.")

        if deseja_alterar_senha:
            if not nova_senha:
                self.add_error("new_password1", "Informe a nova senha.")
            if not confirmacao_nova_senha:
                self.add_error("new_password2", "Confirme a nova senha.")
            if senha_atual and nova_senha and confirmacao_nova_senha:
                if nova_senha != confirmacao_nova_senha:
                    self.add_error("new_password2", "As novas senhas não coincidem.")
                else:
                    username = self.user.username
                    if username.casefold() == self.user.email.casefold():
                        username = email
                    candidate = User(
                        username=username,
                        email=email,
                        first_name=data.get("nickname", self.user.first_name),
                        last_name=self.user.last_name,
                    )
                    try:
                        validate_password(nova_senha, candidate)
                    except forms.ValidationError as error:
                        self.add_error("new_password1", error)
        return data

    def save(self):
        self.user.first_name = self.cleaned_data["nickname"]
        # Contas criadas pelo cadastro público usam o e-mail como usuário.
        # Mantém os dois dados sincronizados, sem mudar usuários independentes
        # como o "admin" do superusuário.
        if self.user.username.casefold() == self.user.email.casefold():
            self.user.username = self.cleaned_data["email"]
        self.user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("new_password1"):
            self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user
