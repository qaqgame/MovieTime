from Main.models import *
MovieTypeDict={'Action':1,'Adventure':2,'Animation':3,"Children's":4,'Comedy':5,'Crime':6,'Documentary':7,'Drama':8,'Fantasy':9,'Film-Noir':10,'Horror':11,'Musical':12,'Mystery':13,'Romance':14,'Sci-Fi':15,'Thriller':16,'War':17,'Western':18,'Others':19}

# 获取type对应的编号
def GetNoOfMovieType(type):
    return MovieTypeDict[type]

# 导入电影
def ImportMovie(title,typeList,length,origin,company,director,content,tagList,actorList,time,imdb,tmdb,cover=None):
    # 获取最终的类型
    temp=1
    finalType=0
    for type in typeList:
        typeNo=GetNoOfMovieType(type)
        finalType=finalType | (temp<<typeNo)


    instance=Movie.objects.create(MovName=title,MovLength=length,MovOrigin=origin,MovType=finalType,MovCompany=company,
                         MovDirector=director, MovDescription=content,MovDate=time,MovImdbId=imdb,MovTmdbId=tmdb)
    # 处理封面
    if cover !=None:
        instance.MovImg=cover

    # 保存电影
    instance.save()

    movId=instance.MovId

    # 处理tag
    for tag in tagList:
        # 查询tag
        queryResult=MovieTag.objects.get(MovTagCnt=tag)
        # 如果为空则先添加该tag
        if queryResult.exists():
            tagInstance=MovieTag.objects.create(MovTagCnt=tag)
            tagInstance.save()
            queryResult=tagInstance
        # 获取tag的id
        realTagId=queryResult.MovTagId

        # 添加MovTagConnection
        connInstance=MovTagConnection.objects.create(MovId=movId,MovTagId=realTagId)
        connInstance.save()

    # 处理演员
    for actor in actorList:
        # 查询演员
        queryResult=Actor.objects.get(ActorName=actor)
        # 如果为空则先添加该tag
        if queryResult.exists():
            actorInstance = Actor.objects.create(ActorName=actor)
            actorInstance.save()
            queryResult = actorInstance
        actorId=queryResult.ActorId

        # 添加演出信息
        actConn=ActorConnection.objects.create(MovId=movId,ActorId=actorId)
        actConn.save()