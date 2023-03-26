from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.db.models import F, Q
from django.db.models.constraints import UniqueConstraint, CheckConstraint
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    username = models.CharField(
        max_length=settings.UNIVERSAL_FIELD_LENGTH,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
        verbose_name='Юзернейм'
        )
    email = models.EmailField(
        max_length=settings.EMAIL_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=settings.UNIVERSAL_FIELD_LENGTH,
        validators=(UnicodeUsernameValidator(),),
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=settings.UNIVERSAL_FIELD_LENGTH,
        validators=(UnicodeUsernameValidator(),),
        verbose_name='Фамилия пользователя'
    )
    password = models.CharField(
        max_length=settings.UNIVERSAL_FIELD_LENGTH,
        verbose_name='Пароль пользователя'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='self_follow_forbidden'
            )

        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        def __str__(self):
            return f'Пользователь {self.user} подписался на {self.author}.'
