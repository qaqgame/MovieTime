# Generated by Django 2.1.2 on 2020-07-05 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0007_auto_20200705_2329'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewrecord',
            name='Email',
            field=models.IntegerField(default=0),
        ),
    ]