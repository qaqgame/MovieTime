# Generated by Django 2.1.2 on 2020-06-29 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userControl', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IDCount',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
