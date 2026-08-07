from django.contrib import admin

from .models import Membros, Recipe

admin.site.register(Membros)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "prep_time", "difficulty", "rating", "is_featured")
    list_filter = ("category", "difficulty", "is_featured")
    search_fields = ("title", "category")
