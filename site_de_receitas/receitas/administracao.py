from django.contrib import admin as administracao

from .modelos import Avaliacao, Favorito, Membro, Receita


administracao.site.register(Membro)


@administracao.register(Receita)
class AdministracaoReceita(administracao.ModelAdmin):
    list_display = (
        "titulo",
        "categoria",
        "tempo_preparo",
        "dificuldade",
        "nota",
        "em_destaque",
    )
    list_filter = ("categoria", "dificuldade", "em_destaque")
    search_fields = ("titulo", "categoria")
    fieldsets = (
        (
            "Informações principais",
            {"fields": ("titulo", "categoria", "url_imagem", "descricao")},
        ),
        (
            "Preparo",
            {"fields": ("tempo_preparo", "dificuldade", "ingredientes", "modo_preparo")},
        ),
        ("Publicação", {"fields": ("nota", "em_destaque")}),
    )


@administracao.register(Favorito)
class AdministracaoFavorito(administracao.ModelAdmin):
    list_display = ("usuario", "receita", "criado_em")
    search_fields = ("usuario__username", "receita__titulo")


@administracao.register(Avaliacao)
class AdministracaoAvaliacao(administracao.ModelAdmin):
    list_display = ("receita", "usuario", "nota", "atualizada_em")
    list_filter = ("nota",)
    search_fields = ("receita__titulo", "usuario__username", "comentario")
