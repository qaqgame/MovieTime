from Main.models import Movie
from Main.utils import GetFilmList
from Main.models import CosRelation

def ImportRelation(id1,id1Origin,id2,id2Origin,relation):
    # movId1='Mov'+str(id1)
    # movId2='Mov'+str(id2)

    # 如果存在则直接结束
    if CosRelation.objects.filter(Movie1=id1,Movie2=id2).exists():
        return

    #否则添加
    CosRelation.objects.create(Movie1=id1,Movie1Origin=id1Origin,Movie2=id2,Movie2Origin=id2Origin,Relation=relation)

# 获得推荐电影列表：电影id，推荐数目,筛选类型
def GetRecommList(ids,count,type):
    result=[]
    tempList=[]
    tempRecoms=[]
    #如果是列表，进行遍历添加
    if isinstance(ids,list):
        for mid in ids:
            tempRelation=CosRelation.objects.filter(Movie1=mid)
            if tempRelation.exists():
                tempRecoms.append(mid)
    else:
        tempRelation = CosRelation.objects.filter(Movie1=ids)
        if not tempRelation.exists():
            return None
        tempRecoms.append(ids)

    #获取原电影数目
    originCount=tempRecoms.count()
    #tempRecoms=CosRelation.objects.filter(Movie1=id).order_by('-Relation')

    # # 如果数量足够则直接取
    # if tempRecoms.count()>count:
    #     for i in range(0,count):
    #         result.append(tempRecoms[i].Movie2)
    #     return result
    # else:
    # 添加进查询队列
    for temp in tempRecoms:
        t=CosRelation()
        t.Movie1=''
        t.Movie2=temp
        tempList.append(t)

    while len(result) <count+originCount and len(tempList)>0:
        tempMov=tempList.pop()
        # 不在则添加
        if tempMov.Movie2 not in result:
            tm=Movie.objects.filter(MovId=tempMov.Movie2)
            if not tm.exists():
                continue
            # 存在该推荐电影则添加
            tempType=tm[0].MovType
            if (tempType&type)!=0:
                result.append(tempMov.Movie2)
        # 查询间接推荐
        tempRecoms=CosRelation.objects.filter(Movie1=tempMov.Movie2).order_by('Relation')
        for temp in tempRecoms:
            tempList.append(temp)
    #移除原电影
    for mid in ids:
       result.remove(mid)


    return result


# 根据类型获取推荐
def GetRecommByType(type,count):

    #获取该类型下按分数排序的电影列表
    tempList=GetFilmList(type=type,order=5)
    if tempList.count()>count:
        return tempList[0:count-1]
    return tempList