from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Membros(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    telefone = models.IntegerField (null=True, blank=True)
    data_ingresso = models.DateField(null=True, blank=True)
   
    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Recipe(models.Model):
    title = models.CharField("titulo", max_length=160)
    category = models.CharField("categoria", max_length=60)
    image_url = models.URLField("imagem", max_length=500)
    prep_time = models.PositiveIntegerField("tempo de preparo (minutos)")
    difficulty = models.CharField("dificuldade", max_length=20, default="Fácil")
    rating = models.DecimalField("avaliação", max_digits=2, decimal_places=1, default=4.5)
    description = models.TextField("descrição", blank=True)
    ingredients = models.TextField("ingredientes", blank=True, help_text="Um ingrediente por linha.")
    preparation = models.TextField("modo de preparo", blank=True, help_text="Um passo por linha.")
    is_featured = models.BooleanField("em destaque", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-rating", "title"]
        verbose_name = "receita"
        verbose_name_plural = "receitas"

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="favorite_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "recipe"), name="unique_user_recipe_favorite")]
        verbose_name = "favorito"
        verbose_name_plural = "favoritos"


class Review(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="recipe_reviews")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField("estrelas", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("comentário", max_length=1000, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "recipe"), name="unique_user_recipe_review")]
        ordering = ["-updated_at"]
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"
