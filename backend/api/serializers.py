from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (
    AmountImgredientsInRecipe, FavoriteRecipe, Ingredient,
    Recipe, ShoppingCart, Tag
)
from users.models import User


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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


class UserSetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128, min_length=8)

    def validate_current_password(self, value):
        user = self.context.get('request').user
        if user.check_password(value):
            return value
        raise serializers.ValidationError(
            'Указан неверный текущий пароль.'
        )

    def validate_new_password(self, value):
        if not value:
            raise serializers.ValidationError(
                'Введите новый пароль'
            )
        validate_password(value)
        return value

    def create(self, validate_data):
        user = self.context.get('request').user
        newpassword = validate_data.get('new_password')
        user.set_password(newpassword)
        user.save()
        return validate_data


class FollowSerializer(UserReadSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(*args):
        """Проверка подписки."""
        return True

    def get_recipes_count(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()

    def get_recipes(self, object):
        queryset = object.recipes.all()[:3]
        return GetFollowerRecipeSerializer(queryset, many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )
        model = Recipe

    def get_ingredients(self, obj):
        """получаем ингредиенты."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('amount_ingredient__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        """Проверка избранного."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
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

    @transaction.atomic
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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
