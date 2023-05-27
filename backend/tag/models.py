from django.db import models


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(
        verbose_name='Название тэга',
        max_length=200,
        blank=True,
        unique=True,
    )

    color = models.TextField(
        verbose_name='Цвет в HEX',
        max_length=7,
        blank=True,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Уникальная строка',
        max_length=200,
        blank=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name
