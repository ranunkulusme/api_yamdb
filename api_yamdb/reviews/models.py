from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from .validations import validate_score


class User(AbstractUser):
    CHOICES = (
        ('user', 'пользователь'),
        ('moderator', 'модератор'),
        ('admin', 'администратор'),
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


class Genre(models.Model):
    """Класс для описания жанров в бд"""
    #  возможно нужно сделать массив строк
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    """Класс для описания категорий в бд"""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return f'{self.name}'


class Title(models.Model):
    """Класс для описания произведений в бд"""
    YEAR_CHOICES = [(r, r) for r in range(0, datetime.date.today().year + 1)]
    name = models.TextField('Имя', max_length=200)
    year = models.IntegerField(('Year'), choices=YEAR_CHOICES,
                               default=datetime.datetime.now().year)
    #  author = models.ForeignKey(User, on_delete=models.CASCADE,
    #                             related_name='titles')
    description = models.TextField('Описание', null=True)
    genre = models.ManyToManyField(
        Genre, related_name="titles1",
        blank=True, null=True,
    )
    category = models.ForeignKey(
        Category, related_name="titles",
        #  не знаю как будет себя вести DO_NOTHING
        on_delete=models.DO_NOTHING,
        blank=True, null=True,
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Отзывы к произведениям
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='ID произведения'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        blank=True, null=True,
        validators=[validate_score],
        help_text='Оценка может быть от 0 до 10'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_author_title'
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    """
    Комментарии к отзывам на произведения
    """
    review = models.ForeignKey(
        Review,
        related_name='comments',
        verbose_name='ID отзыва',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        max_length=250,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации комментария', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
