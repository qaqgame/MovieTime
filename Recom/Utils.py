
from Recom.models import CosRelation

def ImportRelation(id1,id1Origin,id2,id2Origin,relation):
    # movId1='Mov'+str(id1)
    # movId2='Mov'+str(id2)

    # 如果存在则直接结束
    if CosRelation.objects.filter(Movie1=movId1,Movie2=movId2).exists():
        return

    #否则添加
    CosRelation.objects.create(Movie1=movId1,Movie1Origin=id1Origin,Movie2=movId2,Movie2Origin=id2Origin,Relation=relation)

# 获得推荐电影列表：电影id，推荐数目
def GetRecommList(id,count):
    result=[]
    tempList=[]
    tempRecoms=CosRelation.objects.filter(Movie1=id).order_by('-Relation')
    # 如果数量足够则直接取
    if tempRecoms.count()>count:
        for i in range(0,count):
            result.append(tempRecoms[i].Movie2)
        return result
    else:
        for temp in tempRecoms:
            tempList.append(temp)

    while len(result) <count and len(tempList)>0:
        tempMov=tempList.pop()
        # 不在则添加
        if tempMov.Movie2 not in result:
            result.append(temp.Movie2)
        # 查询间接推荐
        tempRecoms=CosRelation.objects.filter(Movie1=tempMov.Movie2).order_by('-Relation')
        for temp in tempRecoms:
            tempList.append(temp)

    return result
