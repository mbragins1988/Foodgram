from django.contrib import admin

from .models import (FavoriteRecipe, Ingredients, RecipeIngredient, Recipes,
                     ShoppingCart)


@admin.register(Ingredients,)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)


@admin.register(Recipes,)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    list_filter = ("author", "name", "tags")


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipe",
        "ingredient",
        "amount",
    )


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recipe",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recipe",
    )
