import json

from django.core.management import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    '''
    Заполнение БД модели Ingredient предоставленными данными
    Создаем миграции
    Заполняем БД командой python manage.py import_date
    '''

    help = 'Импорт данных из ingredients.json в таблицу recipes_ingredient'

    def handle(self, *args, **kwargs):
        with open('data/ingredients.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for row in data:
            account = Ingredients(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            account.save()
