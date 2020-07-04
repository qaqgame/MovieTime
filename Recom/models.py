from django.db import models


# Create your models here.
class CosRelation(models.Model):
    Movie1=models.CharField(verbose_name='电影1id')
    Movie2=models.CharField(verbose_name='电影2id')
    Relation=models.FloatField(verbose_name='相关系数')

    class Meta:
        unique_together=['Movie1','Movie2']
        index_together=['Movie1','Movie2']