# Generated by Django 3.2.15 on 2023-05-26 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipes_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название рецепта'),
        ),
    ]
