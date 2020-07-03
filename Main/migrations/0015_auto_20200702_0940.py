# Generated by Django 3.0.7 on 2020-07-02 01:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0014_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='HasView',
            field=models.BooleanField(default=False, verbose_name='是否有过浏览记录'),
        ),
        migrations.CreateModel(
            name='ViewRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RecordId', models.CharField(blank=True, editable=False, max_length=100, unique=True, verbose_name='实体id')),
                ('TargetId', models.CharField(max_length=50, verbose_name='目标id')),
                ('RecordTime', models.DateTimeField(auto_now_add=True)),
                ('UserId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Main.User', to_field='UserId', verbose_name='用户id')),
            ],
            options={
                'abstract': False,
                'index_together': {('UserId', 'TargetId')},
            },
        ),
    ]
