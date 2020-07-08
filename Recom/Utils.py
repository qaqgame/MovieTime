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
    print("GetRecommList ", len(ids))
    #如果是列表，进行遍历添加
    if isinstance(ids,list):
        print("GetRecommList3")
        for mid in ids:
            realId = Movie.objects.filter(MovId=mid)[0].MovOriginId
            tempRelation=CosRelation.objects.filter(Movie1Origin=realId)
            if tempRelation.exists():
                tempRecoms.append(realId)
    else:
        realId = Movie.objects.filter(MovId=ids)[0].MovOriginId
        tempRelation = CosRelation.objects.filter(Movie1Origin=realId)
        if not tempRelation.exists():
            return None
        tempRecoms.append(realId)

    #获取原电影数目
    originCount=tempRecoms.__len__()
    print("GetRecommList2 ", originCount)
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
        t.Movie2=''
        t.Movie2Origin = temp
        tempList.append(t)

    newRes = []
    while len(result) <count+originCount and len(tempList)>0:
        tempMov=tempList.pop()
        # 不在则添加
        if tempMov.Movie2Origin not in newRes:
            print("klll",tempMov.Movie2Origin)
            tm=Movie.objects.filter(MovOriginId=tempMov.Movie2Origin)
            if not tm.exists():
                continue
            print("Comolll4")
            # 存在该推荐电影则添加
            tempType=tm[0].MovType
            newRes.append(tempMov.Movie2Origin)
            if (tempType&type)!=0:
                result.append(tm[0].MovId)
        # 查询间接推荐
        tempRecoms=CosRelation.objects.filter(Movie1Origin=tempMov.Movie2Origin).order_by('Relation')
        for temp in tempRecoms:
            if temp.Movie2Origin != tempMov.Movie2Origin:
                tempList.append(temp)
    #移除原电影
    for mid in ids:
        if mid in result:
            result.remove(mid)


    return result


# 根据类型获取推荐
def GetRecommByType(type,count):

    #获取该类型下按分数排序的电影列表
    tempList=GetFilmList(type=type,order=5,length=count)
    if tempList.count()>count:
        return tempList[0:count-1]
    return tempList