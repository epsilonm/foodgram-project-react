# Generated by Django 3.2 on 2023-03-28 19:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=150, validators=[django.core.validators.RegexValidator(regex='^[\\w.@+-]+')], verbose_name='Название ингредиента'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(regex='^[\\w.@+-]+')], verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(db_index=True, max_length=150, unique=True, validators=[django.core.validators.RegexValidator(regex='^[\\w.@+-]+')], verbose_name='Название тэга'),
        ),
    ]