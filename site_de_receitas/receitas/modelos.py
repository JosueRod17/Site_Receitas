from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Membro(models.Model):
    primeiro_nome = models.CharField(max_length=255)
    sobrenome = models.CharField(max_length=255)
    telefone = models.IntegerField(null=True, blank=True)
    data_ingresso = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "membro"
        verbose_name_plural = "membros"

    def __str__(self):
        return f"{self.primeiro_nome} {self.sobrenome}"


class Receita(models.Model):
    titulo = models.CharField("título", max_length=160)
    categoria = models.CharField("categoria", max_length=60)
    url_imagem = models.URLField("imagem", max_length=500)
    tempo_preparo = models.PositiveIntegerField("tempo de preparo (minutos)")
    dificuldade = models.CharField("dificuldade", max_length=20, default="Fácil")
    nota = models.DecimalField("nota", max_digits=2, decimal_places=1, default=4.5)
    descricao = models.TextField("descrição", blank=True)
    ingredientes = models.TextField(
        "ingredientes",
        blank=True,
        help_text="Um ingrediente por linha.",
    )
    modo_preparo = models.TextField(
        "modo de preparo",
        blank=True,
        help_text="Um passo por linha.",
    )
    em_destaque = models.BooleanField("em destaque", default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em", "-nota", "titulo"]
        verbose_name = "receita"
        verbose_name_plural = "receitas"

    def __str__(self):
        return self.titulo


class Favorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receitas_favoritas",
    )
    receita = models.ForeignKey(
        Receita,
        on_delete=models.CASCADE,
        related_name="favoritos",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "receita"),
                name="favorito_unico_por_usuario_e_receita",
            )
        ]
        verbose_name = "favorito"
        verbose_name_plural = "favoritos"


class Avaliacao(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avaliacoes_enviadas",
    )
    receita = models.ForeignKey(
        Receita,
        on_delete=models.CASCADE,
        related_name="avaliacoes",
    )
    nota = models.PositiveSmallIntegerField(
        "estrelas",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField("comentário", max_length=1000, blank=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "receita"),
                name="avaliacao_unica_por_usuario_e_receita",
            )
        ]
        ordering = ["-atualizada_em"]
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"
