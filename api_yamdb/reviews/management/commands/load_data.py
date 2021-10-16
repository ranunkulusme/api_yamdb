import csv

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comments, Genre, Review, Title, User


class Command(BaseCommand):
    """
    Команда загружает данные в базу данных из файла csv.
    Параметры:
        --path - путь до файлы, абсолютный
        --model - название модели как в проекте, только с маленькой буквы,
        примеры: 'category': Category,
                'genres': Genre,
                'titles': Title,
                'reviews': Review,
                'comments': Comments,
                'user': User
    Пример использования:
    py manage.py load_data
    --path "/Users/ranunkulus/Dev/YaP/API/api_yamdb/api_yamdb/static/data/category.csv"
    --model categories
    """
    help = (
        'Первым аргументом введите абсолютный путь к файлу, вторым название '
        'модели как в проекте с маленькой буквы'
    )

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='+', type=str)
        parser.add_argument('--model', nargs='+', type=str)

    def handle(self, *args, **options):
        dct_models = {
            'category': Category,
            'genre': Genre,
            'title': Title,
            'review': Review,
            'comments': Comments,
            'user': User
        }
        for csv_file in options['path']:
            print(options)
            reader = csv.reader(open(csv_file), delimiter=',')
            header = reader.__next__()
            model = dct_models[options['model'][0]]
            print(model)
            for row in reader:
                _object_dict = {
                    key: value for key, value in zip(header, row) if key !='id'
                }
                print(_object_dict)
                try:
                    title = model.objects.create(
                        **_object_dict
                    )
                except Title.DoesNotExist:
                    raise CommandError('Poll "%s" does not exist' % row)
                title.save()

                self.stdout.write(
                    'Created employee {}'.format(_object_dict)
                )
