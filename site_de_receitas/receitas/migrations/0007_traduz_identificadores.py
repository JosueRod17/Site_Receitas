"""Traduz os identificadores dos modelos sem recriar as tabelas existentes."""

from django.conf import settings
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("receitas", "0006_review"),
    ]

    operations = [
        # As constraints apontam para os nomes antigos dos campos. Elas precisam
        # sair antes dos RenameField para que a remoção consiga localizar os
        # Campos históricos ``user`` e ``recipe``.
        migrations.RemoveConstraint(
            model_name="favorite",
            name="unique_user_recipe_favorite",
        ),
        migrations.RemoveConstraint(
            model_name="review",
            name="unique_user_recipe_review",
        ),
        migrations.RenameModel(
            old_name="Recipe",
            new_name="Receita",
        ),
        migrations.RenameModel(
            old_name="Favorite",
            new_name="Favorito",
        ),
        migrations.RenameModel(
            old_name="Review",
            new_name="Avaliacao",
        ),
        migrations.RenameModel(
            old_name="Membros",
            new_name="Membro",
        ),
        migrations.RenameField(
            model_name="membro",
            old_name="firstname",
            new_name="primeiro_nome",
        ),
        migrations.RenameField(
            model_name="membro",
            old_name="lastname",
            new_name="sobrenome",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="title",
            new_name="titulo",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="category",
            new_name="categoria",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="image_url",
            new_name="url_imagem",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="prep_time",
            new_name="tempo_preparo",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="difficulty",
            new_name="dificuldade",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="rating",
            new_name="nota",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="description",
            new_name="descricao",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="ingredients",
            new_name="ingredientes",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="preparation",
            new_name="modo_preparo",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="is_featured",
            new_name="em_destaque",
        ),
        migrations.RenameField(
            model_name="receita",
            old_name="created_at",
            new_name="criada_em",
        ),
        migrations.RenameField(
            model_name="favorito",
            old_name="user",
            new_name="usuario",
        ),
        migrations.RenameField(
            model_name="favorito",
            old_name="recipe",
            new_name="receita",
        ),
        migrations.RenameField(
            model_name="favorito",
            old_name="created_at",
            new_name="criado_em",
        ),
        migrations.RenameField(
            model_name="avaliacao",
            old_name="user",
            new_name="usuario",
        ),
        migrations.RenameField(
            model_name="avaliacao",
            old_name="recipe",
            new_name="receita",
        ),
        migrations.RenameField(
            model_name="avaliacao",
            old_name="rating",
            new_name="nota",
        ),
        migrations.RenameField(
            model_name="avaliacao",
            old_name="comment",
            new_name="comentario",
        ),
        migrations.RenameField(
            model_name="avaliacao",
            old_name="updated_at",
            new_name="atualizada_em",
        ),
        migrations.AlterField(
            model_name="favorito",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="receitas_favoritas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="favorito",
            name="receita",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favoritos",
                to="receitas.receita",
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="avaliacoes_enviadas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="receita",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="avaliacoes",
                to="receitas.receita",
            ),
        ),
        migrations.AlterField(
            model_name="receita",
            name="titulo",
            field=models.CharField(max_length=160, verbose_name="título"),
        ),
        migrations.AlterField(
            model_name="receita",
            name="nota",
            field=models.DecimalField(
                decimal_places=1,
                default=4.5,
                max_digits=2,
                verbose_name="nota",
            ),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="nota",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ],
                verbose_name="estrelas",
            ),
        ),
        migrations.AlterModelOptions(
            name="membro",
            options={
                "verbose_name": "membro",
                "verbose_name_plural": "membros",
            },
        ),
        migrations.AlterModelOptions(
            name="receita",
            options={
                "ordering": ["-criada_em", "-nota", "titulo"],
                "verbose_name": "receita",
                "verbose_name_plural": "receitas",
            },
        ),
        migrations.AlterModelOptions(
            name="avaliacao",
            options={
                "ordering": ["-atualizada_em"],
                "verbose_name": "avaliação",
                "verbose_name_plural": "avaliações",
            },
        ),
        migrations.AddConstraint(
            model_name="favorito",
            constraint=models.UniqueConstraint(
                fields=("usuario", "receita"),
                name="favorito_unico_por_usuario_e_receita",
            ),
        ),
        migrations.AddConstraint(
            model_name="avaliacao",
            constraint=models.UniqueConstraint(
                fields=("usuario", "receita"),
                name="avaliacao_unica_por_usuario_e_receita",
            ),
        ),
    ]
