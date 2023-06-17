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
from api.serializers import (
    FollowSerializer, UserReadSerializer, UserWriteSerializer
)
from users.models import Follow

from api.serializers import (
    IngredientSerializer, RecipeWriteSerializer,
    RecipeReadSerializer, TagSerializer
)
from .mixins import ListRetrieveViewSet
from recipes.models import (
    FavoriteRecipe, AmountImgredientsInRecipe, Ingredient,
    Recipe, ShoppingCart, Tag
)
from .paginators import PageNumberPaginator

User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюха для подписок."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user).select_related('follower')


class UserViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserReadSerializer
        return UserWriteSerializer

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)

    def get_queryset(self):
        return User.objects.all()

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


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюха для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюха для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageNumberPaginator

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        """Метод добавляет рецепт в избранное, либо удаляет его."""
        return self.toggle_favorite(request, kwargs, 'favorite')

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, **kwargs):
        """Метод добавляет рецепт в список покупок, или удаляет его."""
        return self.toggle_favorite(request, kwargs, 'shopping_cart')

    def toggle_favorite(self, request, kwargs, favorite_type):
        """
        Метод добавляет/удаляет рецепт из избранного или список покупок.
        """
        user = self.request.user
        recipe = self.get_object()

        toggle_obj = None
        if favorite_type == 'favorite':
            toggle_obj = FavoriteRecipe.objects
        toggle_obj = ShoppingCart.objects

        favorite_obj = toggle_obj.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if favorite_obj:
                return Response(
                    {'message': settings.RECIPE_ALREADY_IN_FAVORITES},
                    status=status.HTTP_400_BAD_REQUEST
                )

            toggle_obj.update_or_create(user=user, recipe=recipe)
            return Response(
                {'message': settings.RECIPE_ADDED_TO_FAVORITES_SUCCESSFULLY},
                status=status.HTTP_201_CREATED
            )

        if not favorite_obj:
            return Response(
                {'message': settings.IS_NOT_IN_FAVORITES_OR_DELETED}
            )

        get_object_or_404(toggle_obj, user=user, recipe=recipe).delete()

        if favorite_type == 'favorite':
            message = settings.SUCCESSFULLY_REMOVED_FROM_FAVORITES
        elif favorite_type == 'shopping_cart':
            message = settings.SUCCESSFULLY_REMOVED_FROM_SHOPPING_LIST

        return Response(
            {'message': message},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """ Метод скачивает корзину покупок."""
        ingredients = AmountImgredientsInRecipe.objects.filter(
            recipe__in_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount_ingredient=Sum('amount'))

        shopping = (
            f'{request.user.username}, {settings.DOWNLOAD_SHOPPING_CART}\n'
        )
        shopping += '\n'.join([
            f'- {amount_ingredient["ingredient__name"]} '
            f'({amount_ingredient["ingredient__measurement_unit"]})'
            f' - {amount_ingredient["amount_ingredient"]}'
            for amount_ingredient in ingredients
        ])
        filename = f'{request.user.username}_shopping.txt'
        response = HttpResponse(shopping, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
