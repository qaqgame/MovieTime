from django.db import models


# Create your models here.
class CosRelation(models.Model):
    Movie1=models.CharField(verbose_name='电影1id',max_length=50)
    Movie1Origin=models.CharField(verbose_name='电影1原始id',max_length=50)
    Movie2=models.CharField(verbose_name='电影2id')
    Movie2Origin=models.CharField(verbose_name='电影2原始id',max_length=50)
    Relation=models.FloatField(verbose_name='相关系数')

    class Meta:
        unique_together=['Movie1','Movie2']
        index_together=['Movie1','Movie2']