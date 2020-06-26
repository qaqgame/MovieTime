from io import BytesIO
from sqlite3 import IntegrityError, DatabaseError
from urllib.request import urlopen

import requests
from django.core.files import File

from Main.models import *
MovieTypeDict={'Action':1,'Adventure':2,'Animation':3,"Children's":4,'Comedy':5,'Crime':6,'Documentary':7,'Drama':8,'Fantasy':9,'Film-Noir':10,'Horror':11,'Musical':12,'Mystery':13,'Romance':14,'Sci-Fi':15,'Thriller':16,'War':17,'Western':18,'Others':19,
               '古装':1, '动画':2, '冒险':3, '犯罪':4, '奇幻':5, '家庭':6, '恐怖':7, '传记':8, '科幻':9, '惊悚':10,'爱情':11, '历史':12, '歌舞':13, '战争':14, '动作':15,  '舞台艺术':16, '西部':17,  '音乐':18, '悬疑':19,  '运动':20, '儿童':21, '武侠':22, '灾难':23, '戏曲':24, '情色':25, '短片':26, '鬼怪':7,  '喜劇 Comedy':27 , '悬念':19, '惊栗':10, '荒诞':28, '其他':29 }
MovieTypeList=['其他','古装','动画','冒险','犯罪','奇幻','家庭','恐怖','传记','科幻','惊悚','爱情','历史','歌舞','战争','动作','舞台艺术','西部','音乐','悬疑','运动','儿童','武侠','灾难','戏曲','情色','短片','喜剧','荒诞']
SexDict={'男':1,'女':2,'未知':3}

RegionDict={'中国大陆':0,'美国':1,'韩国':2,'法国':1,'中国香港':0,'意大利':1,'德国':1,'英国':1,'爱尔兰':1,'中国台湾':0,'印度':3,'葡萄牙':1,'日本':2,'西班牙':1,'加拿大':1,'丹麦':1,
            '罗马尼亚':1, '比利时':1, '瑞典':1,'荷兰':1,'芬兰':1,'挪威':1,'希腊':1,'瑞士':1,'中国澳门':0,'泰国':3,'台灣':0,'Taiwan':0, '英國':1,'UK':1, '印度India':3,'Finland':1,
            '南韩':3,'印度indian':3,'法國':1,'France':1,'加拿大Canada':1,'美國':1,'USA':1, '加拿大canada':1,'中國大陸China':0, '中國大陸':0, 'China':0,'india':3,
            '德國':1,'Germany':1, 'indian':3, 'USA（NBC电视网）':1,'USA（FOX电视网）':1,'USA（ABC电视网）':1,'Colombia':1,'United':1,'中国':0,'香港':0, 'BBC':1,
            '八一电影制片厂':0}
RegionList=['国产','欧美','日韩','印泰','其他']
# 获取type对应的编号
def GetNoOfMovieType(type):
    if not type in MovieTypeDict.keys():
        return 0
    return MovieTypeDict[type]


# 获取区域的编号
def GetReigionCode(region):
    if not region in RegionDict.keys():
        return 4
    return RegionDict[region]

# 获取对应性别编号
def GetNoOfSex(sex):
    if not sex in SexDict.keys():
        return 3
    return SexDict[sex]

# 导入电影
def ImportMovie(title,typeList,length,origin,company,director,content,tagList,actorList,time,imdb,tmdb,cover=None):
    if typeList:
        # 获取最终的类型
        temp=1
        finalType=0
        for type in typeList:
            typeNo=GetNoOfMovieType(type)
            finalType=finalType | (temp<<typeNo)
    else:
        finalType=1

    if origin:
        #处理区域
        finalRegion=0
        for region in origin:
            regionCode=GetReigionCode(region)
            finalRegion=finalRegion|(temp<<regionCode)
    else:
        finalRegion=16

    if company is None:
        company='未知'

    if not imdb:
        imdb=0

    if not content:
        content='无'

    movieInstance=Movie.objects.create(MovName=title,MovLength=length,MovOrigin=finalRegion,MovType=finalType,MovCompany=company,
                         MovDirector=director, MovDescription=content,MovDate=time,MovImdbId=imdb,MovTmdbId=tmdb)
    # 处理封面
    if cover:
        headers={'user - agent': 'Mozilla / 5.0(Windows NT 10.0;\
        Win64;\
        x64) AppleWebKit / 537.36(KHTML, like\
        Gecko) Chrome / 83.0\
        .4103\
        .116\
        Safari / 537.36'}
        r = requests.get(cover,headers=headers)
        io = BytesIO(r.content)
        file = File(io)

        movieInstance.MovImg.save("{0}.{1}".format(title,cover.split('.').pop()),file)
        # 保存电影
        movieInstance.save()



    if tagList:
        # 处理tag
        for tag in tagList:
            # 查询tag
            queryResult=MovieTag.objects.filter(MovTagCnt=tag)
            # 如果为空则先添加该tag
            if not queryResult.exists():
                tagInstance=MovieTag.objects.create(MovTagCnt=tag)
                tagInstance.save()
            else:
                tagInstance=queryResult[0]

            tempQuery=MovTagConnection.objects.filter(MovId=movieInstance,MovTagId=tagInstance)
            if tempQuery.exists():
                print('already exist:',title,'$',tag)
                continue
            else:
                # 添加MovTagConnection
                connInstance=MovTagConnection.objects.create(MovId=movieInstance,MovTagId=tagInstance)
                connInstance.save()

    if actorList:
        # 处理演员
        for actor in actorList:
            # 查询演员
            queryResult=Actor.objects.filter(ActorName=actor)
            # 如果为空则先添加该tag
            if not queryResult.exists():
                actorInstance = Actor.objects.create(ActorName=actor)
                actorInstance.save()
            else:
                actorInstance=queryResult[0]

            tempQuery = ActorConnection.objects.filter(MovId=movieInstance,ActorId=actorInstance)
            if tempQuery.exists():
                continue
            else:
                # 添加演出信息
                actConn=ActorConnection.objects.create(MovId=movieInstance,ActorId=actorInstance)
                actConn.save()
    print('import movie:',movieInstance.MovId," ",title)

def ImportActor(actorName,sex,area):
    sexNo=GetNoOfSex(sex)
    instance=Actor.objects.create(ActorName=actorName,ActorSex=sexNo,ActorArea=area)
    #instance.save()


