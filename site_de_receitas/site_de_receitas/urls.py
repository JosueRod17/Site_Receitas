"""Rotas principais do projeto Site de Receitas."""

from django.contrib import admin as administracao_django
from django.urls import include as incluir, path as caminho


# O nome ``urlpatterns`` é o contrato esperado pelo Django.
urlpatterns = [
    caminho("admin/", administracao_django.site.urls),
    caminho("", incluir("receitas.urls")),
]
