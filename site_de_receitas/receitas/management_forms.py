from django import forms
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from .models import Favorite, Membros, Recipe, Review


class RecipeManagementForm(forms.ModelForm):
    """Recipe fields that are editable in the management area.

    The public rating intentionally does not appear here: it is calculated from
    real user feedbacks.
    """

    class Meta:
        model = Recipe
        fields = [
            "title",
            "category",
            "image_url",
            "prep_time",
            "difficulty",
            "description",
            "ingredients",
            "preparation",
            "is_featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "ingredients": forms.Textarea(attrs={"rows": 7}),
            "preparation": forms.Textarea(attrs={"rows": 7}),
            "image_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "prep_time": forms.NumberInput(attrs={"min": 1}),
        }


class MemberManagementForm(forms.ModelForm):
    class Meta:
        model = Membros
        fields = ["firstname", "lastname", "telefone", "data_ingresso"]
        widgets = {
            "telefone": forms.NumberInput(attrs={"min": 0}),
            "data_ingresso": forms.DateInput(attrs={"type": "date"}),
        }


class ReviewManagementForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["recipe", "user", "rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 5}),
        }


class FavoriteManagementForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ["user", "recipe"]


class UserManagementForm(forms.ModelForm):
    password = forms.CharField(
        label="Nova senha",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Obrigatória para uma nova conta. Deixe em branco para manter a senha atual.",
    )
    email = forms.EmailField(required=False)

    class Meta:
        model = User
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

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.original_username = self.instance.username
        self.original_email = self.instance.email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        if User.objects.filter(email__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nome de usuário já está sendo usado como e-mail.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not email:
            return email
        if User.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not cleaned_data.get("password"):
            self.add_error("password", "Informe uma senha para a nova conta.")
        if cleaned_data.get("password"):
            candidate = User(
                username=cleaned_data.get("username", self.instance.username),
                email=cleaned_data.get("email", self.instance.email),
                first_name=cleaned_data.get("first_name", self.instance.first_name),
                last_name=cleaned_data.get("last_name", self.instance.last_name),
            )
            try:
                validate_password(cleaned_data["password"], candidate)
            except forms.ValidationError as error:
                self.add_error("password", error)
        if self.actor and self.instance.pk == self.actor.pk:
            protected_fields = ("is_active", "is_staff", "is_superuser")
            if any(not cleaned_data.get(field) for field in protected_fields):
                raise forms.ValidationError(
                    "Você não pode remover seu próprio acesso administrativo por este painel."
                )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if (
            self.original_username.casefold() == self.original_email.casefold()
            and self.cleaned_data["username"].casefold() == self.original_username.casefold()
        ):
            user.username = user.email
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            self.save_m2m()
        return user


class GroupManagementForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "permissions"]
        widgets = {"permissions": forms.CheckboxSelectMultiple}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Group.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Já existe um grupo com este nome.")
        return name
