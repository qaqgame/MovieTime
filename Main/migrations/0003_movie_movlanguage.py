# Generated by Django 2.1.2 on 2020-07-03 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0002_remove_movie_movlanguage'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='MovLanguage',
            field=models.CharField(default='未知', max_length=50, verbose_name='电影语言'),
        ),
    ]
