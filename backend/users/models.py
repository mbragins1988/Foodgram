from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='email адрес',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        help_text='Введите пароль',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('pk',)
        constraints = (
            models.UniqueConstraint(fields=('email', 'username'),
                                    name='unique_auth'),
        )

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('-pk',)
        constraints = (
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_follow'),
        )

    def __str__(self):
        return self.user
