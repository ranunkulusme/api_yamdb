from django.contrib.auth.models import AbstractUser
from django.db import models


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
