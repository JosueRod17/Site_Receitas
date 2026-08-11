"""Ponto de entrada ASGI do projeto Site de Receitas."""

import os as sistema_operacional

from django.core.asgi import get_asgi_application as obter_aplicacao_asgi


sistema_operacional.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "site_de_receitas.settings"
)

# ``application`` é o nome exigido por servidores ASGI.
application = obter_aplicacao_asgi()
