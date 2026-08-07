from django.db import migrations


DETAILS = {
    "Macarrão ao Alho e Óleo": ("Uma receita rápida, aromática e perfeita para qualquer dia.", "200 g de espaguete\n3 dentes de alho fatiados\n4 colheres de azeite\nSal e pimenta a gosto\nSalsinha picada", "Cozinhe o macarrão em água salgada até ficar al dente.\nAqueça o azeite e doure o alho em fogo baixo.\nMisture o macarrão escorrido ao azeite.\nFinalize com pimenta e salsinha."),
    "Omelete de Queijo e Tomate": ("Omelete leve e cheia de sabor para começar bem o dia.", "2 ovos\n1 tomate pequeno picado\n2 colheres de queijo ralado\nSal e pimenta a gosto", "Bata os ovos com sal e pimenta.\nAqueça uma frigideira antiaderente.\nAdicione os ovos, tomate e queijo.\nDobre a omelete e cozinhe até o queijo derreter."),
    "Frango Grelhado com Limão": ("Frango suculento com um toque cítrico e ervas frescas.", "2 filés de frango\nSuco de 1 limão\n1 dente de alho\nAzeite, sal e ervas", "Tempere o frango com limão, alho, sal e ervas.\nAqueça uma frigideira com azeite.\nGrelhe os filés dos dois lados até dourar.\nSirva ainda quente."),
    "Bolo de Caneca de Chocolate": ("Sobremesa individual pronta em poucos minutos.", "4 colheres de farinha\n3 colheres de açúcar\n2 colheres de chocolate em pó\n4 colheres de leite\n2 colheres de óleo", "Misture os ingredientes secos na caneca.\nAcrescente leite e óleo até ficar homogêneo.\nLeve ao micro-ondas por cerca de 90 segundos.\nEspere um minuto antes de servir."),
}


def seed_details(apps, schema_editor):
    Recipe = apps.get_model("receitas", "Recipe")
    for title, (description, ingredients, preparation) in DETAILS.items():
        Recipe.objects.filter(title=title).update(
            description=description,
            ingredients=ingredients,
            preparation=preparation,
        )


class Migration(migrations.Migration):
    dependencies = [("receitas", "0004_recipe_description_recipe_ingredients_and_more")]
    operations = [migrations.RunPython(seed_details, migrations.RunPython.noop)]
