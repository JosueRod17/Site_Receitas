from django import forms
from django.contrib.auth.models import User

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
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "As senhas não coincidem.")
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["nickname"],
            password=self.cleaned_data["password1"],
        )


class ProfileForm(forms.Form):
    nickname = forms.CharField(max_length=30)
    current_password = forms.CharField(required=False, widget=forms.PasswordInput)
    new_password1 = forms.CharField(required=False, min_length=8, widget=forms.PasswordInput)
    new_password2 = forms.CharField(required=False, widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["nickname"].initial = user.first_name

    def clean(self):
        data = super().clean()
        password_fields = (data.get("current_password"), data.get("new_password1"), data.get("new_password2"))
        if any(password_fields):
            if not all(password_fields):
                raise forms.ValidationError("Preencha todos os campos de senha para alterá-la.")
            if not self.user.check_password(data["current_password"]):
                self.add_error("current_password", "A senha atual está incorreta.")
            if data["new_password1"] != data["new_password2"]:
                self.add_error("new_password2", "As novas senhas não coincidem.")
        return data

    def save(self):
        self.user.first_name = self.cleaned_data["nickname"]
        if self.cleaned_data.get("new_password1"):
            self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user
