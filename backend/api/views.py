from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .paginators import PageNumberPagination
from users.models import Follow
from api.serializers import (
    IngredientSerializer, RecipeWriteSerializer, FollowSerializer,
    UserReadSerializer, RecipeReadSerializer, TagSerializer,
    UserWriteSerializer, GetFollowerRecipeSerializer, UserSetPasswordSerializer
)
from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAdminOrAuthorOrReadOnly
from .mixins import ListRetrieveViewSet
from recipes.models import (
    FavoriteRecipe, AmountImgredientsInRecipe, Ingredient,
    Recipe, ShoppingCart, Tag
)

User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюха для подписок."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user).select_related('follower')


class UsersViewSet(UserViewSet):
    """Вьюха для юзеров."""
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return UserReadSerializer
        return UserWriteSerializer

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)

    def get_queryset(self):
        return User.objects.all()

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,),
        url_name='set_password'
    )
    def set_password(self, request):
        """Метод меняет пароль."""
        serializer = UserSetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Пароль успешно изменен'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Метод выводит подписки пользователя."""
        pages = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=FollowSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        """Метод добавляет автора в подписки, либо удаляет его."""
        user = request.user
        author = self.get_object()

        if request.method == 'POST':
            follow_obj_filter = Follow.objects.filter(
                user=user,
                author=author
            ).exists()

            if user == author:
                return Response(
                    {'message': settings.YOU_CANT_SUBSCRIBE_TO_YOURSELF},
                    status=status.HTTP_400_BAD_REQUEST
                )

            elif follow_obj_filter:
                return Response(
                    {'message': settings.YOU_ALREADY_SIGNED_UP},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follow.objects.create(user=user, author=author)
            return Response(
                {'message': settings.YOU_HAVE_SUCCESSFULLY_SUBSCRIBED},
                status=status.HTTP_201_CREATED
            )

        follow = Follow.objects.filter(user=user, author=author).exists()
        if follow:
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(
                {'message': settings.YOU_HAVE_SUCCESSFULY_UNSUBCRIBED},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': settings.NOT_SUBSCRIBED},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(ListRetrieveViewSet):
    """Вьюха для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюха для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюха для рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filterset_class = RecipeFilter
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        models = model.objects.filter(user=request.user, recipe=recipe)
        if models.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model(user=request.user, recipe=recipe).save()
        serializer = GetFollowerRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        models = model.objects.filter(user=request.user, recipe=recipe)
        if models.exists():
            models.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    )
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(FavoriteRecipe, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(FavoriteRecipe, request, kwargs.get('pk'))

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request, kwargs.get('pk'))

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """ Метод скачивает корзину покупок."""
        ingredients = AmountImgredientsInRecipe.objects.filter(
            recipe__is_in_shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('amount')

        shopping = (
            f'{request.user.username}, {settings.DOWNLOAD_SHOPPING_CART}\n'
        )
        shopping += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        filename = f'{request.user.username}_shopping.txt'
        response = HttpResponse(shopping, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
