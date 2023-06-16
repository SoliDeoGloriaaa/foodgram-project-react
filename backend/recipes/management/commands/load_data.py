import csv
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Заполняем базу данных ингредиентами."""
    def handle(self, *args, **options):
        try:
            with open(
                f'{settings.BASE_DIR}/data/ingredients.csv',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.reader(csv_file)

                for row in reader:
                    try:
                        obj, created = Ingredient.objects.get_or_create(
                            name=row[0],
                            measurement_unit=row[1],
                        )
                        if not created:
                            print(
                                f'Ингредиент {obj} уже существует в базе.'
                            )
                    except Exception as error:
                        print(f'Ошибка в строке {row}: {error}')
            return (
                f'{Ingredient.objects.count()} ингредиентов успешно загружено'
            )
        except Exception as error:
            raise Exception(f'Неудалось заполнить базу данных: {error}')
