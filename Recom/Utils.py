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
            tempRelation=CosRelation.objects.filter(Movie1=mid)
            if tempRelation.exists():
                realId=tempRelation[0].Movie1Origin
                tempRecoms.append(realId)
    else:
        tempRelation = CosRelation.objects.filter(Movie1=ids)
        if not tempRelation.exists():
            return None
        realId=tempRelation[0].Movie1Origin
        tempRecoms.append(realId)

    #获取原电影数目
    originCount=tempRecoms.__len__()
    print("GetRecommList2 ", originCount)
    for temp in tempRecoms:
        t=CosRelation()
        t.Movie1=''
        t.Movie2=''
        t.Movie2Origin = temp
        tempList.append(t)

    #每部收藏的推荐数
    cnt=int(count/(len(tempList)))+1

    newRes = []
    while len(result) <count+originCount and len(tempList)>0:
        tempCnt=cnt
        tempMov=tempList.pop()
        # 不在则添加
        if tempMov.Movie2Origin not in newRes:
            tm=Movie.objects.filter(MovOriginId=tempMov.Movie2Origin)
            if not tm.exists():
                continue
            # 存在该推荐电影则添加
            tempType=tm[0].MovType
            newRes.append(tempMov.Movie2Origin)
            if (tempType&type)!=0:
                result.append(tm[0].MovId)
                tempCnt-=1
        if len(tempList)<2*(count+originCount):
            # 查询间接推荐
            tempRecoms=CosRelation.objects.filter(Movie1Origin=tempMov.Movie2Origin).order_by('Relation')
            for temp in tempRecoms:
                if tempCnt<=0:
                    break
                if temp.Movie2Origin != tempMov.Movie2Origin:
                    tempList.append(temp)
                    tempCnt-=1
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