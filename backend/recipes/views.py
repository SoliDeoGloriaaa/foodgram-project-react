from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (
    IngredientSerializer, RecipeWriteSerializer,
    RecipeReadSerializer, TagSerializer
)
from .mixins import ListRetrieveViewSet
from .models import (
    FavoriteRecipe, AmountImgredientsInRecipe, Ingredient,
    Recipe, ShoppingCart, Tag
)
from .paginators import PageNumberPaginator


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

    @action(detail=True, methods=['post', 'delete'],)
    def add_or_delete_recipe(self, request, pk, modelserializer):
        """Метод создаёт рецепт, либо удаляет его."""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk).pk
            serializer = modelserializer(
                data={
                    'user': request.user.id,
                    'recipe': recipe
                },
                context={'request': request}
            )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            recipe = get_object_or_404(
                user=request.user,
                recipe=get_object_or_404(Recipe, pk=pk)
            )
            self.perform_destroy(recipe)
            return Response(
                {'message': settings.RECIPE_DELETE},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        """Метод добавляет рецепт в избранное, либо удаляет его."""
        user = self.request.user
        recipe = self.get_object()
        favorite_obj = FavoriteRecipe.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if favorite_obj:
                return Response(
                    {'message': settings.RECIPE_ALREADY_IN_FAVORITES},
                    status=status.HTTP_400_BAD_REQUEST
                )

            FavoriteRecipe.objects.update_or_create(user=user, recipe=recipe)
            return Response(
                {'message': settings.RECIPE_ADDED_TO_FAVORITES_SUCCESSFULLY},
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            if not favorite_obj:
                return Response(
                    {'message': settings.IS_NOT_IN_FAVORITES_OR_DELETED}
                )

            get_object_or_404(
                FavoriteRecipe, user=user, recipe=recipe
            ).delete()
            return Response(
                {'message': settings.SUCCESSFULLY_REMOVED_FROM_FAVORITES},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': settings.METHOD_NOT_ALLOWED},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, **kwargs):
        """Метод добавляет рецепт в список покупок, или удаляет его."""
        recipe = self.get_object()
        user = request.user
        shop = ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

        if request.method == 'POST':
            if shop:
                return Response(
                    {'message': settings.ALREADY_ON_SHOPPING_LIST},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                {'message': settings.RECIPE_ADDDED_TO_CART},
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if not shop:
                return Response(
                    {'message': settings.IS_NOT_IN_SHOPPING_LIST_OR_DELETED},
                    status=status.HTTP_400_BAD_REQUEST
                )

            get_object_or_404(ShoppingCart, user=user, recipe=recipe).delete()
            return Response(
                {'message': settings.SUCCESSFULLY_REMOVED_FROM_SHOPPING_LIST},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': settings.METHOD_NOT_ALLOWED},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """ Метод скачивает корзину покупок."""
        ingredients = AmountImgredientsInRecipe.objects.filter(
            recipe__in_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount_ingredient=Sum('amount_ingredients'))

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
