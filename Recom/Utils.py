import random

from Main.models import Movie, FavoriteRecord
from Main.utils import GetFilmList
from Main.models import CosRelation
import numpy as np

movies_index = np.loadtxt('movies_index.csv', dtype = np.int, delimiter=',')
dic = np.load('movies_dic.npy', allow_pickle=True).item()

def ImportRelation(id1,id1Origin,id2,id2Origin,relation):
    # movId1='Mov'+str(id1)
    # movId2='Mov'+str(id2)

    # 如果存在则直接结束
    if CosRelation.objects.filter(Movie1=id1,Movie2=id2).exists():
        return

    #否则添加
    CosRelation.objects.create(Movie1=id1,Movie1Origin=id1Origin,Movie2=id2,Movie2Origin=id2Origin,Relation=relation)


def _addToQueue(queue,item,cnt,score):
    for i in queue:
        if i['item'].MovId==item.MovId:
            i['power']+=cnt
            return
    temp={}
    temp['item']=item
    temp['power']=cnt
    temp['score']=score
    queue.append(temp.copy())

def _getFromQueue(queue,item):
    for i in queue:
        if i['item'].MovId==item.MovId:
            return i
    return None

# 获得推荐电影列表：电影id，推荐数目,筛选类型
def GetRecommList(ids,count,type):
    # tempList = []
    # firstQueue = []
    # print("GetRecommList ", len(ids))
    # # 如果是列表，进行遍历添加
    # if isinstance(ids, list):
    #     num = int(count / len(ids)) + 1
    #     final = []
    #     for mid in ids:
    #         mov = Movie.objects.filter(MovId=mid)[0]
    #
    #         realId = mov.MovOriginId
    #         tempRelation = CosRelation.objects.filter(Movie1Origin=realId)
    #         rlist = list(tempRelation)
    #         random.shuffle(rlist)
    #         result=[]
    #         for r in rlist:
    #             t=Movie.objects.filter(MovOriginId=movies_index[int(r.Movie2Origin)])[0]
    #             result.append(t.MovId)
    #         final.extend(result[:num])
    #     return final[:count]
    #
    # else:
    #     mov = Movie.objects.filter(MovId=ids)[0]
    #     realId = mov.MovOriginId
    #     tempRelation = CosRelation.objects.filter(Movie1Origin=realId)
    #     if tempRelation.exists():
    #         rlist = list(tempRelation)
    #         random.shuffle(rlist)
    #         return rlist[:count]
    #     else:
    #         return None
    result=[]
    tempList=[]
    firstQueue = []
    print("GetRecommList ", len(ids))
    #如果是列表，进行遍历添加
    if isinstance(ids,list):
        print("GetRecommList3")
        for mid in ids:
            mov = Movie.objects.filter(MovId=mid)[0]
            realId=mov.MovOriginId
            tempRelation=CosRelation.objects.filter(Movie1Origin=realId)
            if tempRelation.exists():
                tempItm={}
                tempItm['power']=100.0
                tempItm['item']=mov
                tempItm['score']=10.0
                firstQueue.append(tempItm.copy())
    else:
        mov = Movie.objects.filter(MovId=ids)[0]
        realId=mov.MovOriginId
        tempRelation = CosRelation.objects.filter(Movie1Origin=realId)
        if not tempRelation.exists():
            return None
        tempItm = {}
        tempItm['power'] = 100.0
        tempItm['item'] = mov
        tempItm['score']=10.0
        firstQueue.append(tempItm.copy())

    # 二级推荐队列
    secondQueue=[]

    print(len(firstQueue))
    size=len(firstQueue)
    #当二级队列足够或一级过长时终止
    while len(secondQueue)<count and len(firstQueue)<size*count and len(firstQueue)>0:
        item=firstQueue.pop()
        mov=item['item']
        # 获取所有推荐
        allRecomm = CosRelation.objects.filter(Movie1Origin=mov.MovOriginId).order_by('Relation')
        print('get recom:'+str(len(allRecomm)))
        parentPower=item['power']
        # 加入一级列表
        for rec in allRecomm:
            realMovs=Movie.objects.filter(MovOriginId=movies_index[int(rec.Movie2Origin)])
            if realMovs.exists():
                realMov=realMovs[0]
                # 计算权重
                power = float(parentPower) / 2

                # 如果类型满足
                if realMov.MovType&int(type)!=0:
                    # 如果满足类型，则加入二级列表
                    if (realMov.MovId not in ids) and(realMov not in tempList) and(realMov.MovType&type!=0) and(realMov.MovScore>0):
                        t=_getFromQueue(firstQueue,realMov)
                        tempPower=power
                        if  t:
                            tempPower = t['power'] + power
                            firstQueue.remove(t)
                        _addToQueue(secondQueue,realMov,tempPower,realMov.MovScore)
                        tempList.append(realMov)
                        continue
                    elif (realMov.MovId not in ids) and (realMov in tempList) and(realMov.MovType&type!=0):
                        _addToQueue(secondQueue,realMov,power,realMov.MovScore)
                        continue
                print('add')
                tempItem={}
                tempItem['power']=power
                tempItem['item']=realMov
                tempItem['score']=realMov.MovScore

                # 否则，直接加入一级列表
                firstQueue.append(tempItem)

    #如果二级列表长度足够
    if len(secondQueue)>=count:
        #直接返回该列表
        result=[]
        secondQueue.sort(key=lambda w:w["power"]*w['score'],reverse=True)
        for i in range(count):
            item=secondQueue[i]
            result.append(item['item'].MovId)
        return result
    #否则，从一级列表取剩下的数量
    restNum=count-len(secondQueue)
    result=[]
    for item in secondQueue:
        result.append(item['item'].MovId)
    if len(firstQueue)>restNum:
        # 排序一级列表
        firstQueue.sort(key=lambda w:w['power']*w['score'],reverse=True)
        for i in range(restNum):
            if firstQueue[i]['item'].MovType&int(type)!=0 and firstQueue[i]['item'].MovScore>0 and (firstQueue[i]['item'].MovId not in ids):
                result.append(firstQueue[i]['item'].MovId)
    #如果不存在
    else:
        # 排序一级列表
        firstQueue.sort(key=lambda w: w['power'] * w['score'], reverse=True)
        for i in firstQueue:
            if i['item'].MovType&int(type)!=0 and i['item'].MovScore>0 and(i['item'].MovId not in ids):
                result.append(i['item'].MovId)
    return result




# 根据类型获取推荐
def GetRecommByType(type,count,user):

    #获取该类型下按分数排序的电影列表

    cnt=0
    result=[]
    while len(result)<count:
        print("get rec by type from:"+str(cnt))
        tempList = list(GetFilmList(type=type, order=5, startIdx=int(cnt),length=count))
        if not tempList:
            break
        random.shuffle(tempList)
        for mov in tempList:
            #检索不在收藏中的电影
            favRec=FavoriteRecord.objects.filter(UserId=user,TargetId=mov.MovId)
            if not favRec.exists():
                result.append(mov)
        cnt+=count
    return result