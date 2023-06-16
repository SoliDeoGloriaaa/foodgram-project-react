from django.contrib import admin

from .models import (
    AmountImgredientsInRecipe, FavoriteRecipe, Ingredient, Recipe, Tag
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    ordering = ('id',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    ordering = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'image',
        'pub_date',
    )
    ordering = ('pub_date',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(AmountImgredientsInRecipe)
admin.site.register(FavoriteRecipe)
