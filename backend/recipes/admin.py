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
        'favorite_count'
    )
    search_fields = ('name', 'author', 'tag')
    list_filter = ('name',)
    inlines = (AmountImgredientsInRecipeAdmin,)
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        return obj.is_favorited.count()


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
        'pub_date',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
    )
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'author',
    )
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(FollowAdmin, Follow)
admin.site.register(FavoriteRecipeAdmin, FavoriteRecipeAdmin)
admin.site.register(AmountImgredientsInRecipe)
admin.site.register(FavoriteRecipe)
