from django.urls import include, path
from rest_framework.routers import SimpleRouter

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UsersViewSet

app_name = 'api'

router = SimpleRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UsersViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
