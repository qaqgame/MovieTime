from django.db import models

# Create your models here.

# 用户manager

class IDCount(models.Model):
    # 类型
    Type=models.CharField(max_length=20,unique=True,verbose_name='id类型')
    # 数字
    Count=models.PositiveIntegerField(default=0,editable=False,verbose_name='计数')
####

class UserManager(models.Manager):
    def create(self, *args, **kwargs):
        instance = IDCount.objects.get(Type='User')
        if not instance.exists():
            cins = IDCount.objects.create(Type='User')
            cins.save()
            instance = cins
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        uId = 'Uid' + str(cnt)
        kwargs['UserId']=uId
        super(UserManager, self).create(*args, **kwargs)
# 用户
class User(models.Model):
    # 用户id
    UserId=models.CharField(max_length=30,verbose_name='用户id',unique=True,editable=False,blank=True)
    # 密码
    UserPwd=models.CharField(max_length=20,verbose_name='密码')
    # 用户名
    UserName=models.CharField(max_length=30,verbose_name='用户名',unique=True)
    # 用户等级
    UserLevel=models.SmallIntegerField(verbose_name='用户等级', default=1)
    # 用户当前经验值
    UserCurExp=models.SmallIntegerField(verbose_name='用户当前经验',default=0)
    # 用户最大经验值
    UserMaxExp=models.SmallIntegerField(verbose_name='用户最大经验',default=1000)
    # 邮箱
    Email = models.EmailField();
    objects=UserManager
    def __str__(self):
        return self.UserName



    class Meta:
        verbose_name='用户信息'
        verbose_name_plural='用户信息'

