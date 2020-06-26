# Generated by Django 3.0.7 on 2020-06-26 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0009_auto_20200624_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='MovDate',
            field=models.DateField(default=1, verbose_name='电影上映时间'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='MovLength',
            field=models.IntegerField(default=0, verbose_name='电影时长'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='MovOrigin',
            field=models.SmallIntegerField(choices=[(1, '国产'), (2, '欧美'), (4, '日韩'), (8, '印泰'), (16, '其他')], default=4, verbose_name='电影产地'),
        ),
    ]