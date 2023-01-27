import csv

from django.core.management.base import BaseCommand, CommandError
from recipies.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загружает данные из .csv и формирует модель Ingredients'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)
        parser.add_argument('--model', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        try:
            model = kwargs['model']
        except model not in {'Ingredient', 'Tag'}:
            raise CommandError('Неверное имя модели')
        try:
            with open(path, 'rt', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',')
                if model == 'Ingredient':
                    for row in reader:
                        Ingredient.objects.create(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                elif model == 'Tag':
                    for row in reader:
                        Tag.objects.create(
                            name=row[0],
                            color=row[1],
                            slug=row[2]
                        )
        except Exception as exc:
            raise (CommandError(exc))

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
