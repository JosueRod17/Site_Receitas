from django.contrib import admin

from .models import Favorite, Membros, Recipe, Review

admin.site.register(Membros)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "prep_time", "difficulty", "rating", "is_featured")
    list_filter = ("category", "difficulty", "is_featured")
    search_fields = ("title", "category")
    fieldsets = (
        ("Informações principais", {"fields": ("title", "category", "image_url", "description")} ),
        ("Preparo", {"fields": ("prep_time", "difficulty", "ingredients", "preparation")} ),
        ("Publicação", {"fields": ("rating", "is_featured")} ),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__title")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user", "rating", "updated_at")
    list_filter = ("rating",)
    search_fields = ("recipe__title", "user__username", "comment")
