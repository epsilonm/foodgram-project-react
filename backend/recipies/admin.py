from django.contrib import admin

from .models import (
    Recipe, Ingredient, Tag, Favorite,
    ShoppingCart, RecipeAmount)
# Register your models here.


class RecipeAmountInline(admin.TabularInline):
    model = RecipeAmount
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Интерфейс управления рецептами."""
    list_display = (
        'name', 'author', 'get_favorite',
        'get_ingredients'
    )
    search_fields = ('name', 'author', 'tags')
    inlines = (RecipeAmountInline, )

    def get_favorite(self, obj):
        return obj.favorite_recipes.count()
    get_favorite.short_description = 'Избранные рецепты'

    def get_ingredients(self, obj):
        return ', '.join([
            ingredient.name for ingredient
            in obj.ingredients.all()
        ])
    get_ingredients.short_description = 'Ингредиенты'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Интерфейс управления ингредиентами."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Интерфейс управления тэгами."""
    fields = (('name', 'color'), 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Интерфейс управления избранным."""
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Интерфейс управления корзинами."""
    list_display = ('user', 'recipe')
