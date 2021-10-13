from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class Users(AbstractUser):
    CHOICES = (
        ('user', 'пользователь'),
        ('moderator', 'модератор'),
        ('admin', 'Администратор'),
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=100,
        choices=CHOICES,
        default=CHOICES[0][0]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]


class Genres(models.Model):
    """Класс для описания жанров в бд"""
    #  возможно нужно сделать массив строк
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return f'{self.title}'


class Categories(models.Model):
    """Класс для описания категорий в бд"""
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return f'{self.title}'


class Titles(models.Model):
    """Класс для описания произведений в бд"""
    YEAR_CHOICES = [(r, r) for r in range(0, datetime.date.today().year + 1)]
    name = models.TextField('Имя', max_length=200)
    year_date = models.IntegerField(('Year'), choices=YEAR_CHOICES,
                                    default=datetime.datetime.now().year)
    # TODO необходимость поля author под вопросом
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='Titles')
    description = models.TextField('Описание', max_length=500)
    genre = models.ForeignKey(
        Genres, related_name="titles1",
        on_delete=models.DO_NOTHING,
        blank=True, null=True,
    )
    category = models.ForeignKey(
        Categories, related_name="titles",
        #  не знаю как будет себя вести DO_NOTHING
        on_delete=models.DO_NOTHING,
        blank=True, null=True,
    )

    def __str__(self):
        return self.name