import random

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


def _addToQueue(queue,item):
    for i in queue:
        if i['item']==item:
            i['power']+=1
            return
    temp={}
    temp['item']=item
    temp['power']=1
    queue.append(temp)

# 获得推荐电影列表：电影id，推荐数目,筛选类型
def GetRecommList(ids,count,type):
    #result=[]
    tempList=[]
    firstQueue = []
    print("GetRecommList ", len(ids))
    #如果是列表，进行遍历添加
    if isinstance(ids,list):
        print("GetRecommList3")
        for mid in ids:
            tempRelation=CosRelation.objects.filter(Movie1=mid)
            if tempRelation.exists():
                mov=Movie.objects.filter(MovId=mid)[0]
                firstQueue.append(mov)
    else:
        tempRelation = CosRelation.objects.filter(Movie1=ids)
        if not tempRelation.exists():
            return None
        mov = Movie.objects.filter(MovId=ids)[0]
        firstQueue.append(mov)
    #
    # #获取原电影数目
    # originCount=tempRecoms.__len__()
    # print("GetRecommList2 ", originCount)
    # for temp in tempRecoms:
    #     t=CosRelation()
    #     t.Movie1=''
    #     t.Movie2=''
    #     t.Movie2Origin = temp
    #     tempList.append(t)
    #
    # #每部收藏的推荐数
    # cnt=int(count/(len(tempList)))+1

    # 二级推荐队列
    secondQueue=[]

    print(len(firstQueue))

    #当二级队列足够或一级过长时终止
    while len(secondQueue)<count and len(firstQueue)<3*count:
        mov=firstQueue.pop()
        # 获取所有推荐
        allRecomm = CosRelation.objects.filter(Movie1Origin=mov.MovOriginId).order_by('Relation')
        print('get recom:'+str(len(allRecomm)))
        # 加入一级列表
        for rec in allRecomm:
            realMovs=Movie.objects.filter(MovOriginId=rec.Movie2Origin)
            print(rec.Movie2Origin)
            if realMovs.exists():
                realMov=realMovs[0]
                # 如果类型满足
                if realMov.MovType&int(type)!=0:
                    # 如果已存在，则加入二级列表
                    if (realMov in firstQueue) and (realMov.MovId not in ids) and(realMov not in tempList):
                        print('add second')
                        firstQueue.remove(realMov)
                        _addToQueue(secondQueue,realMov)
                        tempList.append(realMov)
                        continue
                    elif (realMov in tempList):
                        print('in temp,add second')
                        _addToQueue(secondQueue,realMov)
                        continue
                print('add')
                # 否则，直接加入一级列表
                firstQueue.append(realMov)

    #如果二级列表长度足够
    if len(secondQueue)>=count:
        #直接返回该列表
        result=[]
        secondQueue=secondQueue.sort(key=lambda w:w["power"],reverse=True)
        for i in range(count):
            result.append(secondQueue[i]['item'].MovId)
        return result

    #否则，从一级列表取剩下的数量
    restNum=count-len(secondQueue)
    result=[]
    for item in secondQueue:
        result.append(item['item'].MovId)
    # 随机打乱一级列表
    random.shuffle(firstQueue)
    for i in range(restNum):
        if firstQueue[i].MovType&int(type)!=0:
            result.append(firstQueue[i].MovId)
    return result

    #
    # while (len(result) <(count+originCount)) and len(tempList)>0:
    #
    #     tempCnt=cnt
    #     # 取出首元素
    #     tempMov=tempList.pop()
    #
    #
    #     for recomm in allRecomm:
    #         # 检查二级队列
    #         if recomm in secondQueue
    #
    #     # 不在则添加
    #     if tempMov.Movie2Origin not in newRes:
    #         tm=Movie.objects.filter(MovOriginId=tempMov.Movie2Origin)
    #         if not tm.exists():
    #             continue
    #         # 存在该推荐电影则添加
    #         tempType=tm[0].MovType
    #         newRes.append(tempMov.Movie2Origin)
    #         if (tempType&type)!=0:
    #             result.append(tm[0].MovId)
    #             tempCnt-=1
    #     if len(tempList)<2*(count+originCount):
    #         # 查询间接推荐
    #         tempRecoms=CosRelation.objects.filter(Movie1Origin=tempMov.Movie2Origin).order_by('Relation')
    #         for temp in tempRecoms:
    #             if tempCnt<=0:
    #                 break
    #             if temp.Movie2Origin != tempMov.Movie2Origin:
    #                 tempList.append(temp)
    #                 tempCnt-=1
    # #移除原电影
    # for mid in ids:
    #     if mid in result:
    #         result.remove(mid)
    #
    #
    # return result


# 根据类型获取推荐
def GetRecommByType(type,count):

    #获取该类型下按分数排序的电影列表
    tempList=GetFilmList(type=type,order=5,length=count)
    if tempList.count()>count:
        return tempList[0:count-1]
    return tempList