from io import BytesIO
from sqlite3 import IntegrityError, DatabaseError
from urllib.request import urlopen

import requests
from django.core.files import File
from django.db.models import QuerySet
from Main.models import *

MsgTemplate={'result':True,'reason':'','data':{}}

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
def ImportMovie(title,typeList,length,origin,company,director,content,tagList,actorList,time,imdb,tmdb,language,cover=None):
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

    #创建导演
    directorInstance=CreateActorConn(director)

    movieQuery=Movie.objects.filter(MovName=title,MovLength=length,MovDirector=directorInstance)
    # 若该电影已存在则直接return
    if movieQuery.exists():
        return
    movieInstance=Movie.objects.create(MovName=title,MovLength=length,MovOrigin=finalRegion,MovType=finalType,MovCompany=company,
                         MovDirector=directorInstance, MovDescription=content,MovDate=time,MovImdbId=imdb,MovTmdbId=tmdb,MovLanguage=language)

    # # 处理导演信息
    # tempQuery = ActorConnection.objects.filter(MovId=movieInstance, ActorId=directorInstance)
    # if tempQuery.exists():
    #     return
    # else:
    #     # 添加演出信息
    #     actConn = ActorConnection.objects.create(MovId=movieInstance, ActorId=directorInstance)
    #     actConn.save()

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
            actorInstance=CreateActorConn(actor,movieInstance)
            tempQuery = ActorConnection.objects.filter(MovId=movieInstance, ActorId=actorInstance)
            if tempQuery.exists():
                continue
            else:
                # 添加演出信息
                actConn = ActorConnection.objects.create(MovId=movieInstance, ActorId=actorInstance)
                actConn.save()
    print('import movie:',movieInstance.MovId," ",title)

def ImportActor(actorName,sex,area):
    sexNo=GetNoOfSex(sex)
    instance=Actor.objects.create(ActorName=actorName,ActorSex=sexNo,ActorArea=area)
    #instance.save()

def CreateActorConn(actor):
    # 查询演员
    queryResult = Actor.objects.filter(ActorName=actor)
    # 如果为空则先添加该actor
    if not queryResult.exists():
        actorInstance = Actor.objects.create(ActorName=actor)
        actorInstance.save()
    else:
        actorInstance = queryResult[0]
    return actorInstance


# 根据电影的id获取该电影
def GetFilm(filmId):
    movie=Movie.objects.filter(MovId=filmId)
    if movie.exists():
        return movie[0]
    return None

# 根据电影的id获取电影的标签
def GetFilmTags(filmId):
    tags=MovTagConnection.objects.filter(MovId=filmId)
    tagList=[]
    if tags.exists():
        for t in tags:
           tagList.append(t.MovTagId)
        result=[]
        for tid in tagList:
            result.append(MovieTag.objects.filter(MovTagId=tid)[0].MovTagCnt)
        return result
    return None

# 根据电影id获取演员列表
def GetFilmActors(filmId):
    actors=ActorConnection.objects.filter(MovId=filmId)
    al=[]
    if actors.exists():
        for t in actors:
           al.append(t.MovTagId)
        result=[]
        for aid in al:
            result.append(Actor.objects.filter(ActorId=aid)[0])
        return result
    return None

# 根据电影类型来获取电影列表
def GetFilmByType(type):
    filmList=Movie.objects.extra(where=['MovType&%d!=0'],params=[type])
    result=[]
    for mov in filmList:
        result.append(mov.MovId)
    return result

# 根据电影产地来获取电影列表
def GetFilmByRegion(regions):
    filmList = Movie.objects.extra(where=['MovOrigin&%d!=0'], params=[regions])
    result = []
    for mov in filmList:
        result.append(mov.MovId)
    return result

# 根据电影年份获取列表
def GetFilmByDate(year):
    tempDate = datetime.datetime.strptime(str(year), "%Y")
    realDate = tempDate.date()
    filmList=Movie.objects.filter(MovDate=realDate)
    result = []
    for mov in filmList:
        result.append(mov.MovId)
    return result

# 获取电影列表并排序
def GetFilmList(type,regions,year,order):
    tempDate = datetime.datetime.strptime(str(year), "%Y")
    realDate = tempDate.date()
    filmList = Movie.objects.extra(where=['MovType&%d!=0'], params=[type]).extra(where=['MovOrigin&%d!=0'],params=[regions]).filter(MovDate=realDate)
    #日期升序
    if order==0:
        filmList=filmList.order_by('MovDate')
    # 日期降序
    elif order==1:
        filmList=filmList.order_by('-MovDate')
    # 名称升序
    elif order==2:
        filmList=filmList.order_by('MovName')
    # 名称降序
    elif order==3:
        filmList=filmList.order_by('-MovName')
    result = []
    for mov in filmList:
        result.append(mov.MovId)
    return result

# 获取电影列表(
# 根据导演名搜索电影
# return:QuerySet
def SearchFilmsByDirector(directorName):
    directorInstances=Actor.objects.filter(ActorName=directorName)
    #如果不存在则返回空
    if not directorInstances.exists():
        return None
    films=Movie.objects.filter(MovDirector=directorInstances[0])
    return films

# 封装返回的json
def wrapTheJson(result, reason, data={}):
    res = MsgTemplate.copy()
    res['reason'] = reason
    res['result'] = result
    res['data'] = data
    return res


# 通过用户名获取用户实例
def GetUser(name):
    user = User.objects.filter(UserName=name)
    if user.exists():
        return user[0]
    return None


title = {
    'ViewRecord': '浏览记录',
    'Agree': '点赞记录',
    'EditRecord': '编辑记录',
    'FavoriteRecord': '收藏记录',
    'ReplyRecord': '回复记录',
}


# 映射title
def GetTitle(name):
    return title[name]

# 获取图片url
def GetMovImgUrl(MovInstance):
    imgPath = str(MovInstance.MovImg)
    fileName = imgPath.split('.')[0]
    if fileName.__contains__('default_cover'):
        cover = '/static/cover/default_cover.bmp'
    else:
        ext = imgPath.split('.').pop()
        movId = MovInstance.MovId
        filename = 'Cover_{0}.{1}'.format(movId, ext)
        cover = '/static/cover/' + movId + '/' + filename
    return cover

def wrapTheDetail(name, id):
    if(name == 'ViewRecord'):
        # record = ViewRecord.objects.filter(TargetId=id)[0]
        MovName = Movie.objects.filter(MovId=id)[0].MovName
        return "浏览了" + MovName + "电影"
        # name.objects.filter()
    if name == "AgreeRecord":
        record = Agree.objects.filter(TargetId=id)[0]
        type = ''
        if record.AgreeType == 1:
            type = record.get_AgreeType_display()
            reply = ReplyRecord.objects.filter(RecordId=id)[0]
            # 点赞了电影评论
            # if reply.ReplyType == 1:
            type = reply.get_ReplyType_display() + type
            content = reply.ReplyContent
            return "点赞了" + type + "  " + content
            # else:
            #     type = reply.get_ReplyType_display() + type
            #     content = reply.ReplyContent
            #     return "点赞了"
        # 点赞了标签
        if record.AgreeType == 2:
            record = Agree.objects.filter(TargetId=id)[0]
            type = record.get_AgreeType_display()
            movTag = MovieTag.objects.filter(MovTagId=id)[0]
            return "点赞了" + type + "  " + movTag.MovTagCnt
    if name == 'EditRecord':
        record = EditRecord.objects.filter(TargetId=id)[0]
        # 修改信息
        return record.EditContent
    if name == 'FavoriteRecord':
        record = FavoriteRecord.objects.filter(TargetId=id)[0]
        MovName = Movie.objects.filter(MovId=id)[0].MovName
        return "收藏了" + " 电影 " + MovName
    if name == 'ReplyRecord':
        record = ReplyRecord.objects.filter(TargetId=id)[0]
        # 评论电影
        if record.ReplyType == 1:
            MovName = Movie.objects.filter(MovId=id)[0].MovName
            return "评论了电影 "+ MovName + "\t" + record.ReplyContent


