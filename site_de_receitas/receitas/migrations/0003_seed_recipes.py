from django.db import migrations


RECIPES = [
    ("Macarrão ao Alho e Óleo", "Almoço", "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=700&q=80", 20, "Fácil", 4.9),
    ("Omelete de Queijo e Tomate", "Café da Manhã", "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=700&q=80", 10, "Fácil", 4.7),
    ("Frango Grelhado com Limão", "Jantar", "https://images.unsplash.com/photo-1600891964092-4316c288032e?auto=format&fit=crop&w=700&q=80", 30, "Médio", 4.8),
    ("Bolo de Caneca de Chocolate", "Sobremesas", "https://images.unsplash.com/photo-1579954115563-e72bf1381629?auto=format&fit=crop&w=700&q=80", 8, "Fácil", 4.8),
    ("Salada Caesar Clássica", "Almoço", "https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=700&q=80", 15, "Fácil", 4.5),
    ("Arroz Tropical com Frango", "Almoço", "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=700&q=80", 40, "Médio", 4.9),
    ("Panqueca Americana Fofa", "Café da Manhã", "https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=700&q=80", 20, "Fácil", 4.8),
    ("Sopa de Legumes Caseira", "Jantar", "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=700&q=80", 35, "Fácil", 4.7),
]


def seed_recipes(apps, schema_editor):
    Recipe = apps.get_model("receitas", "Recipe")
    for title, category, image_url, prep_time, difficulty, rating in RECIPES:
        Recipe.objects.get_or_create(
            title=title,
            defaults={
                "category": category,
                "image_url": image_url,
                "prep_time": prep_time,
                "difficulty": difficulty,
                "rating": rating,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("receitas", "0002_recipe")]

    operations = [migrations.RunPython(seed_recipes, migrations.RunPython.noop)]
