from django.core.validators import MinValueValidator
from django.db import models

from tag.models import Tag
from users.models import User


class Ingredients(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('pk',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингридиенты',
        through='RecipeIngredient',
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=250,
        blank=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )

    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = "Рецепты"
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи ингридиентов и рецептов."""

    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=(
            MinValueValidator(1,
                              message='Количество должно быть больше ноля.'),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_recipe',
            ),
        )

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"


class FavoriteRecipe(models.Model):
    """Модель избранное."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites_user',
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_shopping_cart'),
        )

    def __str__(self):
        return (f'Рецепт {self.recipe} добавлен'
                f'в избранное пользователя {self.user}')


class ShoppingCart(models.Model):
    """Модель список покупок."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'Рецепт {self.recipe} добавлен в корзину.'
