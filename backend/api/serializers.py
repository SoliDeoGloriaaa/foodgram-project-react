from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (
    AmountImgredientsInRecipe, FavoriteRecipe, Ingredient,
    Recipe, ShoppingCart, Tag,
)
from users.models import User


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password',
            'username', 'first_name',
            'last_name', 'is_subscribed',
        )

        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj: User):
        """Проверка подписки."""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.follower.filter(author=obj).exists()


class UserWriteSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]',
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class GetFollowerRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserReadSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = GetFollowerRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(*args):
        """Проверка подписки."""
        return True
        # А здесь всегда возвращается True, поэтому так =)

    def get_recipes_count(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AmountImgredientsInRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    in_carts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'in_carts', 'name',
            'image', 'text', 'cooking_time'
        )
        model = Recipe

    def get_ingredients(self, obj):
        """получаем ингредиенты."""
        recipe = obj
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
        )

    def get_is_favorited(self, obj):
        """Проверка избранного."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()

    def get_in_carts(self, obj):
        """Проверка корзины покупок."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = UserWriteSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'author', 'name', 'text',
            'cooking_time'
        )

    def create_ingredients(self, recipe, ingredients):
        AmountImgredientsInRecipe.objects.bulk_create(
            [AmountImgredientsInRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient_id=ingredient['id']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
