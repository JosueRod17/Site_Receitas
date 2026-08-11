"""Ponto de entrada WSGI do projeto Site de Receitas."""

import os as sistema_operacional

from django.core.wsgi import get_wsgi_application as obter_aplicacao_wsgi


sistema_operacional.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "site_de_receitas.settings"
)

# ``application`` é o nome exigido por servidores WSGI.
application = obter_aplicacao_wsgi()
