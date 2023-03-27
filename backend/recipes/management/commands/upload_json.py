import json

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    MODELS = {
        "i": Ingredient,
        "t": Tag
    }
    help = 'Загружает данные из .json и формирует модель'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-t', action="store_true")
        group.add_argument("-i", action="store_true")

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        flag = "t" if kwargs["t"] else "i"
        model = self.MODELS[flag]
        try:
            with open(path, 'rt', encoding='utf-8') as file:
                data = json.loads(file.read())
                for attrs in data:
                    model.objects.get_or_create(**attrs)
        except Exception as exc:
            raise (CommandError(exc))

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
