import os
import time
import datetime

from django.db import models
# Create your models here.
#电影标签实体
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

# 标签Manager
class MovTagManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Tag')
        if not all.exists():
            print('create tag count')
            cins = IDCount.objects.create(Type='Tag')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        tagId = 'Tag' + str(cnt)
        kwargs['MovTagId']=tagId
        return super(MovTagManager, self).create(*args, **kwargs)
# 标签实体
class MovieTag(models.Model):
    MovTagId=models.CharField(max_length=20,unique=True,editable=False,blank=True)
    MovTagCnt=models.CharField(max_length=20,unique=True,verbose_name='标签内容')
    objects = MovTagManager()

    def __str__(self):
        return self.MovTagCnt



    class Meta:
        verbose_name='电影标签'
        verbose_name_plural='电影标签'

# 电影封面路径获取
def cover_directory_path(instance, filename):
    ext = filename.split('.').pop()
    filename = 'Cover_{0}.{1}'.format(instance.MovId, ext)
    return os.path.join('static/cover', instance.MovId,filename)

# 电影manager
class MovieManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Movie')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='Movie')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        movId = 'Mov' + str(cnt)
        kwargs['MovId']=movId
        return super(MovieManager, self).create(*args, **kwargs)

# 电影实体
class Movie(models.Model):
    MovId=models.CharField(max_length=50,unique=True,editable=False,blank=True)
    # 电影名
    MovName=models.CharField(max_length=100,verbose_name='电影标题')
    # 电影类型：
    MovType=models.IntegerField(verbose_name='电影类型')
    # 电影时长:
    MovLength=models.IntegerField(verbose_name='电影时长',default=0)
    # 电影封面
    MovImg=models.ImageField(upload_to=cover_directory_path,verbose_name='电影封面', default='static/cover/default_cover.png')
    # 电影产地
    MovOrigin=models.SmallIntegerField(verbose_name='电影产地',default=16)
    # 电影公司
    MovCompany=models.CharField(max_length=100,verbose_name="电影公司",default='未知')
    # 电影导演
    MovDirector=models.ForeignKey(to='Actor', to_field='ActorId', verbose_name='导演id',null=True,on_delete=models.SET_NULL,default=None)
    # 电影简介
    MovDescription=models.TextField(verbose_name='电影描述',default='无')
    # 电影上映时间
    MovDate=models.DateField(auto_now=False,auto_now_add=False,verbose_name='电影上映时间',default=datetime.MINYEAR)
    # 电影语言
    MovLanguage=models.CharField(max_length=50,verbose_name='电影语言',default='未知')
    # 平均分
    MovScore=models.FloatField(verbose_name='电影平均分',default=0.0)
    # 评分数
    MovScoreCount=models.IntegerField(verbose_name='评分人数',default=0)
    #IMDB id
    MovImdbId=models.IntegerField(verbose_name='IMDB',default=0)
    #tmdb id
    MovTmdbId=models.IntegerField(verbose_name='TMDB',default=0)
    #原始id
    MovOriginId=models.CharField(max_length=50,verbose_name='原始id')

    objects=MovieManager()
    def __str__(self):
        return self.MovName

    class Meta:
        verbose_name='电影信息'
        verbose_name_plural='电影信息'
        managed = True

# 演员manager
class ActorManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Actor')
        if not all.exists():
            print('create actor count')
            cins = IDCount.objects.create(Type='Actor')
            cins.save()
            instance = cins
        else:
            instance=all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        uId = 'Aid' + str(cnt)
        kwargs['ActorId']=uId
        return super(ActorManager, self).create(*args, **kwargs)
# 演员
class Actor(models.Model):
    # 演员id
    ActorId=models.CharField(max_length=50,unique=True,blank=True,verbose_name='演员id')
    # 演员姓名
    ActorName=models.CharField(max_length=50,verbose_name='演员姓名')
    # 演员地区
    ActorArea=models.CharField(max_length=50,verbose_name='演员地区',blank=True,default='未知')
    # 演员性别
    ActorSex=models.SmallIntegerField(choices=[(1,'男'),(2,'女'),(3,'未知')],verbose_name='演员性别',default=3)

    objects=ActorManager()

    def __str__(self):
        return self.ActorName
    class Meta:
        verbose_name_plural=verbose_name='演员信息'

# 演员参演关系
class ActorConnection(models.Model):
    # 演员id
    ActorId = models.ForeignKey(to='Actor', to_field='ActorId', verbose_name='演员id', on_delete=models.CASCADE)
    # 电影id
    MovId = models.ForeignKey(to='Movie', to_field='MovId', verbose_name='电影id', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural=verbose_name='参演/导演信息'
        unique_together=['ActorId','MovId']
        index_together=['ActorId','MovId']

# 用户manager
class UserManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='User')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='User')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        uId = 'Uid' + str(cnt)
        kwargs['UserId']=uId
        return super(UserManager, self).create(*args, **kwargs)
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
    UserCurExp=models.SmallIntegerField(verbose_name='用户当前经验', default=0)
    # 用户最大经验值
    UserMaxExp=models.SmallIntegerField(verbose_name='用户最大经验', default=1000)
    # 邮箱
    Email = models.EmailField()
    Types = models.IntegerField(verbose_name="用户喜欢的类型", default=~(1<<30))
    # 是否有浏览
    HasView=models.BooleanField(default=False,verbose_name='是否有过浏览记录')

    objects=UserManager()
    def __str__(self):
        return self.UserName



    class Meta:
        verbose_name='用户信息'
        verbose_name_plural='用户信息'


        
# 记录类基类
class BaseRecord(models.Model):
    # 记录id
    RecordId=models.CharField(max_length=100,unique=True,verbose_name='实体id',editable=False,blank=True)
    # 记录用户
    UserId=models.ForeignKey(to='User', to_field='UserId',verbose_name='用户id', on_delete=models.CASCADE)
    # 记录目标
    TargetId=models.CharField(max_length=50, verbose_name='目标id')
    # 记录时间
    RecordTime=models.DateTimeField(auto_now_add=True,editable=True)

    class Meta:
        abstract=True
        index_together=['UserId','TargetId']

# 浏览manager
class ViewManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='View')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='View')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        uId = 'View' + str(cnt)
        kwargs['RecordId']=uId
        return super(ViewManager, self).create(*args, **kwargs)

#浏览数据
class ViewRecord(BaseRecord):
    objects=ViewManager()

# 点赞manager
class AgreeManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Agree')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='Agree')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        aId = 'Ag' + str(cnt)
        kwargs['RecordId']=aId
        return super(AgreeManager, self).create(*args, **kwargs)

#点赞数据
class Agree(BaseRecord):
    # 点赞目标类型(评论/标签)
    AgreeType=models.PositiveSmallIntegerField(choices=[(1,'评论'),(2,'标签')], verbose_name='点赞类型')

    objects=AgreeManager()


# 编辑manager
class EditManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Edit')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='Edit')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        eId = 'Edit' + str(cnt)
        kwargs['RecordId']=eId
        return super(EditManager, self).create(*args, **kwargs)
# 编辑记录
class EditRecord(BaseRecord):
    # 编辑类型
    EditType=models.PositiveSmallIntegerField(choices=[(1,'修改信息'),(2,'添加标签')], verbose_name='编辑类型')
    # 编辑内容
    EditContent=models.TextField(verbose_name='修改内容')

    objects=EditManager()

    class Meta:
        verbose_name=verbose_name_plural='编辑记录'

# 收藏manager
class FavManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Fav')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='Fav')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        fId = 'Fav' + str(cnt)
        kwargs['RecordId']=fId
        return super(FavManager, self).create(*args, **kwargs)
# 收藏记录
class FavoriteRecord(BaseRecord):
    # 收藏类型
    FavoriteType=models.PositiveSmallIntegerField(default=1,choices=[(1,'电影')], verbose_name='收藏类型')

    objects=FavManager()

# 评论manager
class ReplyManager(models.Manager):
    def create(self, *args, **kwargs):
        all = IDCount.objects.filter(Type='Reply')
        if not all.exists():
            print('create movie count')
            cins = IDCount.objects.create(Type='Reply')
            cins.save()
            instance = cins
        else:
            instance = all[0]
        cnt = instance.Count
        instance.Count += 1
        instance.save()
        rId = 'Rep' + str(cnt)
        kwargs['RecordId']=rId
        return super(ReplyManager, self).create(*args, **kwargs)

# 评论记录
class ReplyRecord(BaseRecord):
    # 回复目标的类型
    ReplyType=models.PositiveSmallIntegerField(choices=[(1,'电影'),(2,'评论')], verbose_name='回复类型')
    # 评分(可为空)
    ReplyGrade=models.SmallIntegerField(verbose_name='评分',blank=True,null=True)
    # 内容
    ReplyContent=models.TextField(verbose_name='回复内容')
    # 点赞数
    AgreeCount=models.PositiveIntegerField(default=0,editable=False,verbose_name='点赞数')

    objects=ReplyManager()

    class Meta:
        verbose_name=verbose_name_plural='评论记录'

# 电影与标签的联系
class MovTagConnection(models.Model):
    # 标签id
    MovTagId=models.ForeignKey(to='MovieTag',to_field='MovTagId',verbose_name='标签id',on_delete=models.CASCADE)
    # 电影id
    MovId=models.ForeignKey(to='Movie', to_field='MovId', verbose_name='电影id', on_delete=models.CASCADE)
    # 点赞数量
    AgreeCount=models.PositiveIntegerField(default=0, editable=False,verbose_name='点赞数')

    class Meta:
        verbose_name_plural=verbose_name='标签联系信息'
        unique_together=['MovTagId','MovId']
        # 添加联合索引
        index_together=['MovTagId','MovId']

# 相关度
class CosRelation(models.Model):
    Movie1=models.CharField(verbose_name='电影1id',max_length=50)
    Movie1Origin=models.CharField(verbose_name='电影1原始id',max_length=50)
    Movie2=models.CharField(verbose_name='电影2id',max_length=50)
    Movie2Origin=models.CharField(verbose_name='电影2原始id',max_length=50)
    Relation=models.FloatField(verbose_name='相关系数')

    class Meta:
        unique_together=['Movie1','Movie2']
        index_together=['Movie1','Movie2']
# id记录
class IDCount(models.Model):
    # 类型
    Type=models.CharField(max_length=20,unique=True,verbose_name='id类型')
    # 数字
    Count=models.PositiveIntegerField(default=0,editable=False,verbose_name='计数')

    def __str__(self):
        return self.Type
####
#触发器部分
####

# 处理评分
@receiver(pre_save,sender=ReplyRecord)
def Pre_Save_RepRcd_Handler(sender,instance,**kwargs):
    # 如果该评论为电影评分
    if instance._state.adding and instance.ReplyType==1:
        movId=instance.TargetId
        # 查找目标电影
        movInstances=Movie.objects.filter(MovId=movId)
        # 当该电影存在时，进行后续处理
        if movInstances.exists():
            movInstance=movInstances[0]
            # 更新平均分
            allScore=movInstance.MovScore*movInstance.MovScoreCount
            allScore+=instance.ReplyGrade
            realScore=float(allScore)/(movInstance.MovScoreCount+1)
            movInstance.MovScore=realScore
            movInstance.MovScoreCount+=1
            movInstance.save()

# 处理标签删除情况
@receiver(pre_delete,sender=MovieTag)
def Pre_Delete_MovieTag_Handler(sender,instance,**kwargs):
    MovTagConnection.objects.filter(MovTagId=instance.MovTagId).delete()
    # 删除相应的点赞信息
    Agree.objects.filter(TargetId__contains=instance.MovTagId).delete()

#处理电影删除情况
@receiver(pre_delete,sender=Movie)
def Pre_Delete_Movie_Handler(sender,instance,**kwargs):
    #删除相应的点赞信息以及标签联系
    MovTagConnection.objects.filter(MovId=instance.MovTagId).delete()
    # 删除相应的点赞信息
    Agree.objects.filter(TargetId__contains=instance.MovTagId).delete()

# 处理浏览记录创建
@receiver(pre_save,sender=ViewRecord)
def Pre_Save_ViewRcd_Handler(sender,instance,**kwargs):
    # 将该用户的拥有浏览设为true
    user=User.objects.get(UserId=instance.UserId.UserId)
    user.HasView=True
    user.save()

# 处理点赞（在添加点赞时触发)
@receiver(pre_save,sender=Agree)
def Pre_Save_Agree_Handler(sender,instance,**kwargs):
    # 如果点赞的是标签
    if instance._state.adding and instance.AgreeType ==2:
        # 获取目标id
        temp=instance.TargetId
        # 获取id
        tagId,movId=temp.split('#')
        # 查询
        target=MovTagConnection.objects.get(MovTagId=tagId,MovId=movId)
        target.AgreeCount +=1
        target.save()
    # 点赞的是评论
    elif instance._state.adding and instance.AgreeType==1:
        # 获取目标id
        temp = instance.TargetId
        # 查询
        target = ReplyRecord.objects.get(RecordId=temp)
        target.AgreeCount += 1
        target.save()

# 处理取消点赞
@receiver(pre_delete,sender=Agree)
def Pre_Delete_Agree_Handler(sender,instance,**kwargs):
    # 如果点赞的是标签
    if instance.AgreeType == 2:
        # 获取目标id
        temp = instance.TargetId
        # 获取id
        tagId, movId = temp.split('#')
        # 查询
        target = MovTagConnection.objects.get(MovTagId=tagId, MovId=movId)
        target.AgreeCount -= 1
        target.save()
    # 点赞的是评论
    elif instance.AgreeType == 1:
        # 获取目标id
        temp = instance.TargetId
        # 查询
        target = ReplyRecord.objects.get(RecordId=temp)
        target.AgreeCount -= 1
        target.save()

