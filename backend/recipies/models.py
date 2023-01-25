from colorfield.fields import ColorField
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)

from users.models import User


class Tag(models.Model):
    """Модель тэга."""
    name = models.CharField(
        max_length=150,
        db_index=True,
        unique=True,
        verbose_name='Название тэга')
    color = ColorField(
        format='hex',
        max_length=7,
        unique=True,
        verbose_name='HEX-код'
        )
    slug = models.SlugField(
        max_length=150,
        verbose_name='Слаг',
        unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=150,
        verbose_name='Название ингредиента',
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=150
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeAmount',
        verbose_name='Ингредиенты')
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipies')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
        )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                1,
                message='Время готовки должно быть больше минуты!'),
            MaxValueValidator(
                1441,
                message='Время готовки не должно быть больше суток!')
        )
    )
    image = models.ImageField(
        upload_to='recipies/image',
        verbose_name='Изображение'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class FavShopCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_is_unique'
            )
        ]


class Favorite(FavShopCart):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorite_recipes'


class ShoppingCart(FavShopCart):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        default_related_name = 'shopping_carts'


class RecipeAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(
            1,
            message='Количество ингредиентов должно быть больше единицы!'
        ),)

    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количества ингредиентов'

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount}'
            f' ({self.ingredient.measurement_unit})'
        )
