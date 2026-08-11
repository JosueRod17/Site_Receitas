#!/usr/bin/env python
"""Utilitário de linha de comando do Django para o projeto."""

import os as sistema_operacional
import sys as sistema


def executar():
    """Executa as tarefas administrativas solicitadas na linha de comando."""
    sistema_operacional.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "site_de_receitas.settings"
    )
    try:
        from django.core.management import (
            execute_from_command_line as executar_pela_linha_de_comando,
        )
    except ImportError as erro_importacao:
        raise ImportError(
            "Não foi possível importar o Django. Confirme se ele está instalado "
            "e se o ambiente virtual foi ativado."
        ) from erro_importacao
    executar_pela_linha_de_comando(sistema.argv)


if __name__ == "__main__":
    executar()
