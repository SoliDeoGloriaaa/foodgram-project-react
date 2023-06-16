from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.paginators import PageNumberPagination
from api.serializers import UserSerializer, FollowSerializer
from users.models import Follow

User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюха для подписок."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user).select_related('follower')


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюха юзеров."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(
            self.request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        elif request.method == 'DELETE':
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

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Метод выводит подписки пользователя."""
        if self.request.user.is_anonymous:
            return Response(
                {'message': settings.UNAUTHORIZED},
                status=status.HTTP_401_UNAUTHORIZED
            )
        pages = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
