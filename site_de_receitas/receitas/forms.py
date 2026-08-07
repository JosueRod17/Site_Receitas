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
            password=self.cleaned_data["password1"],
        )
