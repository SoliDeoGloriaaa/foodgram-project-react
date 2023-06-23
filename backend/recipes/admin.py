from django.contrib import admin

from .models import (
    AmountImgredientsInRecipe,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    Tag,
    ShoppingCart
)
from users.models import Follow


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'color'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class AmountImgredientsInRecipeAdmin(admin.StackedInline):
    model = AmountImgredientsInRecipe
    autocomplete_fields = ('ingredient',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'image',
        'text',
        'cooking_time',
        'pub_date',
    )
    search_fields = ('name', 'author', 'tag')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class FollownAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',
                    'subscribe_date')
    search_fields = ('user__username', 'author__username')
    list_filter = ('author',)
    empty_value_display = '-пусто-'


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Follow, FavoriteRecipeAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(AmountImgredientsInRecipe)
