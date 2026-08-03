from django import forms

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