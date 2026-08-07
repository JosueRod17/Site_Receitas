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
    is_featured = models.BooleanField("em destaque", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-rating", "title"]
        verbose_name = "receita"
        verbose_name_plural = "receitas"

    def __str__(self):
        return self.title
