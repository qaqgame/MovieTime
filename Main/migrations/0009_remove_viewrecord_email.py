# Generated by Django 2.1.2 on 2020-07-05 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0008_viewrecord_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='viewrecord',
            name='Email',
        ),
    ]
