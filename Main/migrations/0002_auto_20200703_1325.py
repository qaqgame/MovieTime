# Generated by Django 3.0.7 on 2020-07-03 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movie',
            options={'managed': True, 'verbose_name': '电影信息', 'verbose_name_plural': '电影信息'},
        ),
    ]
