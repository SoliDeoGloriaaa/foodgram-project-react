from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=7,
        default='#E26C2D',
        unique=True,
        blank=False,
        null=False,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name='Название',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        null=False,
        blank=False,
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        through='recipes.AmountImgredientsInRecipe',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            settings.MINIMUN_COOKING_TIME,
            message='Минимальное время приготовления - 1 минута.')],
        verbose_name='Время приготовления',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'{self.name}'


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite'
            )
        ]

    def __str__(self):
        return (
            f'{self.user.username} закинул рецепт'
            f'{self.recipe.name} в избранное.'
        )


class AmountImgredientsInRecipe(models.Model):
    """Модель ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='amount_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Ингредиент',
        related_name='amount_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            settings.MINIMUM_INGREDIENT_IN_RECIPE,
            message='Минимальное количество ингредиентов - 1 шт.'
        )],
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]
        ordering = ('recipe', )

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class ShoppingCart(models.Model):
    """Корзина покупок"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В корзине',
        related_name='is_in_shopping_cart',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь списка',
        related_name='carts',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
