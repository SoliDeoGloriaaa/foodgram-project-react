import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', default='secret_key')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', default=True)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'about',
    'core',
    'recipes',
    'api',
    'users',
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 6,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram_project.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MINIMUN_COOKING_TIME = 1
MINIMUM_INGREDIENT_IN_RECIPE = 1


DOWNLOAD_SHOPPING_CART = 'Вот ваш список покупок:'
RECIPE_DELETE = 'рецепт успешно удалён'
METHOD_NOT_ALLOWED = 'метод не разрешен'
UNAUTHORIZED = 'нужна авторизация'
NOT_SUBSCRIBED = 'нельзя отписаться, ведь подписка не оформлена'
YOU_HAVE_SUCCESSFULLY_SUBSCRIBED = 'вы успешно подписались.'
YOU_CANT_SUBSCRIBE_TO_YOURSELF = 'Нельзя подписаться на себя.'
YOU_HAVE_SUCCESSFULY_UNSUBCRIBED = 'Вы успешно отписались'
YOU_ALREADY_SIGNED_UP = 'Вы уже подписаны.'
RECIPE_ADDDED_TO_CART = 'рецепт добавлен в корзину'
IS_NOT_IN_SHOPPING_LIST_OR_DELETED = 'Рецепта нет в корзине, или он уже удален'
SUCCESSFULLY_REMOVED_FROM_SHOPPING_LIST = 'рецепт успешно удалён из корзины'
ALREADY_ON_SHOPPING_LIST = 'рецепт уже в корзине.'
SUCCESSFULLY_REMOVED_FROM_FAVORITES = 'рецепт успешно удалён из избранного'
IS_NOT_IN_FAVORITES_OR_DELETED = 'рецепта нет в избранном, либо он удалён'
RECIPE_ADDED_TO_FAVORITES_SUCCESSFULLY = 'рецепт успешно добавлен в избранное'
RECIPE_ALREADY_IN_FAVORITES = 'рецепт уже в избранном.'
