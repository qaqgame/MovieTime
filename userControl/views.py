from django.shortcuts import render, redirect
from Main.models import *
from Main import models
from django.http import JsonResponse
import json
import random
# Create your views here.
from Main.utils import MsgTemplate, GetMovImgUrl, MovieTypeList, ParseMovieTypes, ParseMovieRegions, GetFilmList, \
    RegionList, ToTypeNum, wrapTheMovie, GetReplies, CreateAgree, CancelAgree, wrapTag, AddUserExp
from Main.utils import GetFilm, wrapTheJson, GetUser, GetTitle, wrapTheDetail
from Recom.Utils import GetRecommList, GetRecommByType
from Recom.Utils import *


def login(request):
    if request.method == 'GET':
        path = request.GET.get('next', '')
    if request.method == 'POST':
        recv_data = json.loads(request.body.decode())  #解析前端发送的JSON格式的数据
        conditions = {
            'UserName': recv_data['name'],   #以键值对的方式获取值
            'UserPwd':  recv_data['pwd'],
        }
        user = models.User.objects.filter(**conditions)
        if user:
            name = recv_data['name']
            # ret = redirect("/index/")
            if not request.session.session_key:
                request.session.create()
            request.session['is_login'] = True
            request.session['user1'] = name
            uins=user[0]
            request.session['level']=uins.UserLevel
            AddUserExp(uins,5)
            # request.session.save()
            print(request.session['user1'])
            # path = request.POST.get('next')
            # path = '/' + path
            # return redirect(path)
            return JsonResponse({"username": name, "result": "success", "reason": "登录成功", "formtype": "login"})
        else:
            return JsonResponse({"password": "false", "result": "failed", "reason": "用户名或密码错误", "formtype": "login"})


def logout(request):
    request.session.flush()
    return JsonResponse({'result': 'success', 'reason': '','data':{'target':'/'}})


def index(request):
    status = request.session.get('is_login')
    if not status:
        return JsonResponse({'hasSes': 'false', 'next': '/ses_index/'})
    else:
        return render(request, 's_index.html')


def getUser(request):
    status = request.session.get('is_login')
    if not status:
        return JsonResponse({'result':'failed','reason':'','data':{'user': '前往登录', 'link': '/'}})
    else:
        username = request.session.get('user1')
        level = request.session.get('level')
        if not username or not level:
            return JsonResponse({'result':'failed','reason':'','data':{'user': '前往登录', 'link': '/'}})
        else:
            return JsonResponse({'result':'success','reason':'','data':{'user': username, 'link': '/user/'+username, 'level': level}})


def signup(request):
    if request.method == 'POST':
        recv_data = json.loads(request.body.decode())
        print(recv_data)
        conditions = {
            'UserName': recv_data['name'],
        }
        res = models.User.objects.filter(**conditions)

        if res:
            return JsonResponse({'result': 'failed', 'reason': '帐号存在', 'formtype': 'register'})
        else:
            user = models.User.objects.create(UserName=recv_data['name'],
                                              UserPwd=recv_data['pwd'],
                                              )
            print(user, type(user))

            return JsonResponse({'signup': 'success', 'result': 'success', 'reason': '注册成功', 'formtype': 'register'})
    return render(request, "signup.html")


def UserSpace(request,un):
    res = MsgTemplate.copy()
    uname=un
    # 存在用户名
    if uname:
        userInstances=models.User.objects.filter(UserName=uname)
        # 如果没找到用户
        if not userInstances.exists():
            res['result']=False
            res['reason']='未找到该用户'
            return JsonResponse(res)
        userInstance=userInstances[0]
        # 处理用户数据
        username=userInstance.UserName
        userlv=userInstance.UserLevel
        usercur=userInstance.UserCurExp
        usermax=userInstance.UserMaxExp
        newUser=not userInstance.HasView
        userData={'username':username,'currlevel':userlv,'currexp':usercur,'maxexp':usermax,"newuser":newUser}
        request.session['level']=userInstance.UserLevel
        # 查询该收藏
        favList=models.FavoriteRecord.objects.filter(UserId=userInstance.UserId)
        print(favList.__len__())
        # 生成收藏数据
        favResultList=[]
        # 遍历收藏列表
        for fav in favList:

            # 获取收藏时间
            date=str(fav.RecordTime)

            MovInstances=models.Movie.objects.filter(MovId=fav.TargetId)
            print(fav.TargetId)
            print(MovInstances.__len__())
            #电影不存在则跳过
            if not MovInstances.exists():
                continue

            # 生成图片路径
            MovInstance = MovInstances[0]
            imgPath=str(MovInstance.MovImg)
            fileName=imgPath.split('.')[0]
            if fileName.__contains__('default_cover'):
                cover='/static/cover/default_cover.png'
            else:
                ext=imgPath.split('.').pop()
                movId=MovInstance.MovId
                filename = 'Cover_{0}.{1}'.format(movId, ext)
                cover='/static/cover/'+movId+'/'+filename

            # 获取电影名
            name=MovInstance.MovName

            movid=MovInstance.MovId
            favResultList.append({'movieimgurl': cover, 'moviename': name,'movieid':movid,'extrainfo': date})


        # 处理session部分


        resultData={'userrelated':userData,'keeprelated':favResultList}
        res['result']=True
        res['data']=resultData
        return JsonResponse(res)
    # 不存在用户名
    res['result']=False
    res['reason']='未收到用户名'
    return JsonResponse(res)


# 浏览记录
def ViewRecord(request, un):
    res = MsgTemplate.copy();
    username = un
    if username != '':
        userInstance = models.User.objects.filter(UserName=username)
        if not userInstance.exists():
            res['reason'] = "用户不存在"
            res['result'] = 'failed'
            return JsonResponse(res)
        userInstance = userInstance[0]
        uid = userInstance.UserId
        viewRecords = models.ViewRecord.objects.filter(UserId=uid)
        if not viewRecords.exists():
            res['reason'] = "暂无浏览记录"
            res['result'] = "success"
            return JsonResponse(res)
        data = {}
        movList = []
        for viewRecord in viewRecords:
            oneMessage = {}
            movid = viewRecord.TargetId
            movieInstance = GetFilm(movid)
            movieName = movieInstance.MovName
            movImg = GetMovImgUrl(movieInstance)
            movViewTime = viewRecord.RecordTime
            oneMessage['movieimgurl'] = movImg
            oneMessage['moviename'] = movieName
            oneMessage['extrainfo'] =  movViewTime
            oneMessage['movieid']=movid
            movList.append(oneMessage)
        movList.sort(key=lambda w:w["extrainfo"],reverse=True)
        data['histories'] = movList
        res['reason'] = ''
        res['result'] = 'success'
        res['data'] = data
        return JsonResponse(res)
    res['reason'] = '没有得到username'
    res['result'] = 'failed'
    return JsonResponse(res)


# 电影详细信息
def movInfo(request, mn):
    movId = mn
    movInstance = models.Movie.objects.filter(MovId=movId)
    if not movInstance.exists():
        res = wrapTheJson("failed", '不存在这部电影')
        return JsonResponse(res)
    movInstance = movInstance[0]
    data = {}
    movieinfo = {}
    movieinfo['name'] = movInstance.MovName
    types = ParseMovieTypes(movInstance.MovType)
    movieinfo['type'] = types
    movieinfo['movtime'] = movInstance.MovDate
    regions=ParseMovieRegions(movInstance.MovOrigin)
    movieinfo['area'] = regions
    if movInstance.MovDirector:
        movieinfo['director'] = movInstance.MovDirector.ActorName
    else:
        movieinfo['director']='未知'
    movieinfo['lastfor'] = movInstance.MovLength
    # 改模型
    movieinfo['lang'] = movInstance.MovLanguage
    movieinfo['coverurl'] = GetMovImgUrl(movInstance)
    movieinfo['description'] = movInstance.MovDescription
    movieinfo['rate'] = movInstance.MovScore

    actorIds = models.ActorConnection.objects.filter(MovId=movInstance.MovId)
    actors = []
    # print(actorIds[0].ActorId, actorIds[0])
    for id in actorIds:
        actor = id.ActorId.ActorName
        actors.append(actor)
    movieinfo['actors'] = actors

    # 评分
    movieinfo['rate'] = movInstance.MovScore
    uid = GetUser(request.session.get('user1'))

    # 获取标签
    tags=MovTagConnection.objects.filter(MovId=movInstance.MovId)
    #获取user
    username = request.session.get('user1', '')
    userInstance = GetUser(username)
    if not userInstance:
        userInstance=None
    tagList=wrapTag(tags,userInstance)
    movieinfo['tags']=tagList
    # print(uid.UserId)
    if not uid:
        ifKeeped = False
    else:
        # uid = GetUser(uname)
        fav = models.FavoriteRecord.objects.filter(UserId=uid, TargetId=movInstance.MovId)
        if not fav:
            ifKeeped = False
        else:
            ifKeeped = True
    movieinfo['ifKeeped'] = ifKeeped
    data['movieinfo'] = movieinfo
    res = wrapTheJson("success", '', data=data)
    if uid:
        viewRecord=models.ViewRecord.objects.filter(UserId=uid, TargetId=movInstance.MovId)
        if not viewRecord:
            models.ViewRecord.objects.create(UserId=uid,TargetId=movInstance.MovId)
            AddUserExp(uid,1)
        else:
            viewRecord[0].RecordTime=datetime.datetime.now()
            viewRecord[0].save()
    return JsonResponse(res)


# 时间线
def timeLine(request, un):
    uid = GetUser(un).UserId
    timelines = []
    for sub in models.BaseRecord.__subclasses__():
        messages = sub.objects.filter(UserId=uid)
        if not messages.exists():
            continue
        for message in messages:
            timeline = {}
            print(message, sub.__name__)
            timeline['actiontime'] = message.RecordTime
            timeline['title'] = GetTitle(sub.__name__)
            tempD=wrapTheDetail(sub.__name__,message.RecordId)
            timeline['origin']=tempD['origin']
            timeline['originid']=tempD['originId']
            timeline['detail'] = tempD['detail']
            if timeline['detail'] == None:
                continue
            timelines.append(timeline)

            # 如果是评论，则查询他人对自己的评论及点赞
            if sub.__name__ == 'ReplyRecord':
                reply = ReplyRecord.objects.filter(RecordId=message.RecordId)[0]
                targetMsg = ReplyRecord.objects.filter(TargetId=message.RecordId)
                if targetMsg.exists():
                    for tm in targetMsg:
                        # 非本人的操作
                        if tm.UserId.UserId is not reply.UserId.UserId:
                            temptl = {}
                            temptl['actiontime'] = tm.RecordTime
                            temptl['title'] = GetTitle(sub.__name__)
                            temptl[
                                'detail'] = tm.UserId.UserName + " 评论了你的回复(" + reply.ReplyContent + "):" + tm.ReplyContent
                            temptl['target'] = tm.UserId.UserName
                            timelines.append(temptl)

                #查询点赞
                targetAgree=Agree.objects.filter(TargetId=message.RecordId)
                if targetAgree.exists():
                    for ta in targetAgree:
                        # 非本人的操作
                        if ta.UserId.UserId is not reply.UserId.UserId:
                            tempag={}
                            tempag['actiontime']=ta.RecordTime
                            tempag['title']=GetTitle('Agree')
                            tempag['detail']=ta.UserId.UserName+' 点赞了你的评论('+reply.ReplyContent+')'
                            tempag['target']=ta.UserId.UserName
                            timelines.append(tempag)

    timelines.sort(key=lambda w:w["actiontime"],reverse=True)
    data = {}
    data['timeline'] = timelines
    res = wrapTheJson("success", "", data=data)
    return JsonResponse(res)

#添加标签
def AddTag(request):
    recv_data = json.loads(request.body.decode())
    movId=recv_data['movid']
    movInstances=Movie.objects.filter(MovId=movId)
    if not movInstances.exists():
        res=wrapTheJson('failed','无法找到该电影：'+movId)
        return JsonResponse(res)
    movIns=movInstances[0]
    tag=recv_data['content']
    instances=MovieTag.objects.filter(MovTagCnt=tag)
    if not instances.exists():
        instance=MovieTag.objects.create(MovTagCnt=tag)
    else:
        instance=instances[0]
    conns=MovTagConnection.objects.filter(MovTagId=instance,MovId=movIns)
    if not conns.exists():
        conn=MovTagConnection.objects.create(MovTagId=instance,MovId=movIns)
    else:
        res=wrapTheJson('failed','标签已存在')
        return JsonResponse(res)
    data={}
    data['tagcontent']=instance.MovTagCnt
    data['agree']=conn.AgreeCount
    data['tagid']=instance.MovTagId
    data['agreed']=False
    res=wrapTheJson('success','',data)
    return JsonResponse(res)


# 显示片库页面
def ShowMoviePage(request):
    typeList=MovieTypeList
    regionList=RegionList
    data={}
    data['typeList']=typeList
    data['regionList']=regionList
    res=wrapTheJson('success','',data=data)
    return JsonResponse(res)

# 搜索
def search(request):
    type = request.GET.get('type', -1)
    # 生成type
    if int(type)==-1:
        typeList=(~(1<<30))
    else:
        typeList=(1<<int(type))
    field = request.GET.get('field', -1)
    # 生成区域
    if int(field)   ==-1:
        regionList=(~(1<<5))
    else:
        regionList=(1<<int(field))
    time = request.GET.get('time', -1)
    moviename = request.GET.get('moviename', '')
    startIdx= request.GET.get('start',0)
    # conditions = {}
    # if type != '':
    #     conditions['MovType'] = type
    # if field != '':
    #     conditions['MovOrigin'] = field
    # if time != '':
    #     conditions['MovDate'] = time
    # if moviename != '':
    #     conditions['MovName'] = moviename
    movies = GetFilmList(typeList,regionList,moviename,5,startIdx,20)
    if not movies.exists():
        res = wrapTheJson("failed", "没有符合条件的电影")
        return JsonResponse(res)
    data = {}
    allmovies = []
    for movie in movies:
        info = {}
        info['movieimgurl'] = GetMovImgUrl(movie)
        info['movieId']=movie.MovId
        info['moviename'] = movie.MovName
        # 需要修改
        info['extrainfo'] = movie.MovScore
        allmovies.append(info)
    data['allmovies'] = allmovies
    res = wrapTheJson("success", "", data=data)
    return JsonResponse(res)

# 点赞
def agree(request):
    target=request.GET.get('target','')
    movName = request.GET.get('movname', '')
    movId = request.GET.get('movid', '')
    if movId=='' and movName!='':
        movInss=Movie.objects.filter(MovName=movName)
        if not movInss.exists():
            res=wrapTheJson('failed','无法找到该电影')
            return JsonResponse(res)
        movIns=movInss[0]
        movId=movIns.MovId
    elif movId=='' and movName=='':
        movId=None

    # 获取点赞目标类型,构造targetid
    tempType = request.GET.get('type', 'Reply')
    if tempType == 'Reply':
        agreeType = 1
        targetId = target
    #如果是标签
    else:
        agreeType = 2
        tag=MovieTag.objects.filter(MovTagId=target)
        if not tag.exists():
            res = wrapTheJson('failed', '无法找到该标签')
            return JsonResponse(res)
        tagId=tag[0].MovTagId
        targetId=tagId

    # 获取用户
    username = request.session.get('user1', '')
    userInstance = GetUser(username)
    if not userInstance:
        res = wrapTheJson('failed', '无法找到该用户')
        return JsonResponse(res)
    else:
        AddUserExp(userInstance,2)
    try:
        result=CreateAgree(userInstance,targetId,agreeType,movId)
        print(result)
    except Exception as e:
        print(e)
        res=wrapTheJson('failed',e.__str__())
        return JsonResponse(res)
    finally:
        data={}
        data['agreecount']=result
        res=wrapTheJson('success','',data)
        return JsonResponse(res)



#取消点赞
def cancelAgree(request):
    target = request.GET.get('target', '')
    movName = request.GET.get('movname', '')
    movId = request.GET.get('movid', '')
    if movId == '' and movName != '':
        movInss = Movie.objects.filter(MovName=movName)
        if not movInss.exists():
            res = wrapTheJson('failed', '无法找到该电影')
            return JsonResponse(res)
        movIns = movInss[0]
        movId = movIns.MovId
    elif movId == '' and movName == '':
        movId = None

    # 获取点赞目标类型,构造targetid
    tempType = request.GET.get('type', 'Reply')
    if tempType == 'Reply':
        agreeType = 1
        targetId = target
    # 如果是标签
    else:
        agreeType = 2
        tag = MovieTag.objects.filter(MovTagId=target)
        if not tag.exists():
            res = wrapTheJson('failed', '无法找到该标签')
            return JsonResponse(res)
        tagId = tag[0].MovTagId
        targetId = tagId

    # 获取用户
    username = request.session.get('user1', '')
    userInstance = GetUser(username)
    if not userInstance:
        res = wrapTheJson('failed', '无法找到该用户')
        return JsonResponse(res)

    try:
        result=CancelAgree(userInstance,targetId,agreeType,movId)
    except Exception as e:
        res=wrapTheJson('failed',e.__str__())
        return JsonResponse(res)
    finally:
        data={}
        data['agreecount']=result
        res=wrapTheJson('success','',data)
        return JsonResponse(res)


def keep(request):
    movieid = request.GET.get("movieid", '')
    if movieid == '':
        res = wrapTheJson("failed", "没有得到电影名")
        return JsonResponse(res)
    movie = models.Movie.objects.filter(MovId=movieid)
    if not movie.exists():
        res = wrapTheJson("failed", "没有该电影名的数据")
        return JsonResponse(res)
    movId = movie[0].MovId
    uid = GetUser(request.session.get('user1'))
    favRecord = models.FavoriteRecord.objects.create(UserId=uid, TargetId=movId)
    res = wrapTheJson("success", '')
    return JsonResponse(res)


def getKeep(request, un):
    user = GetUser(un)
    if user == None:
        return JsonResponse(wrapTheJson("failed", "没有这个用户"))
    uid = user.UserId
    favMovies = models.FavoriteRecord.objects.filter(UserId=uid)
    data = {}
    timeline = []
    for favMovie in favMovies:
        message = {}
        favId = favMovie.TargetId
        movie = models.Movie.objects.filter(MovId=favId)[0]
        # if not movie:
        #     continue
        message['movieimgurl'] = GetMovImgUrl(movie)
        message['moviename'] = movie.MovName
        message['movieid']=movie.MovId
        message['extrainfo'] = favMovie.RecordTime
        timeline.append(message)
    data['keepmovies'] = timeline
    res = wrapTheJson("success", '', data)
    return JsonResponse(res)

#获取该用户的评论
def getUserReply(request,un):
    # username = request.session.get('user1', '')
    username = un
    if username == '':
        res = wrapTheJson('failed', '没有登陆')
        return JsonResponse(res)
    userInstance = GetUser(username)
    replys = models.ReplyRecord.objects.filter(UserId=userInstance.UserId)
    timelines = []
    for record in replys:
        timeline = {}
        # 评论电影
        timeline['actiontime'] = record.RecordTime
        if record.ReplyType == 1:
            MovIns = Movie.objects.filter(MovId=record.TargetId)[0]
            MovName=MovIns.MovName
            Movid=MovIns.MovId
            timeline['origin']=MovName
            timeline['originid']=Movid
            str1 = "评论了电影 " + MovName + ":" +str(record.ReplyGrade)+","+ record.ReplyContent
        else:
            #获取评论目标
            target=ReplyRecord.objects.filter(RecordId=record.TargetId)[0]
            content=target.ReplyContent
            username = target.UserId.UserName
            uid=target.UserId.UserId
            timeline['origin']=username
            timeline['originid']=uid
            str1 = "评论了" + username + "的评论("+content+"):" + record.ReplyContent
        timeline['detail'] = str1
        timelines.append(timeline)
    timelines.sort(key=lambda w: w["actiontime"], reverse=True)
    data = {}
    data['coms'] = timelines
    res = wrapTheJson('success', '', data=data)
    return JsonResponse(res)

def likeType(request):
    recv_data = json.loads(request.body.decode())  # 解析前端发送的JSON格式的数据
    types = recv_data['choosen']
    username = request.session.get("user1", '')
    print("session: ",username)
    if username == '':
        res = wrapTheJson("failed", "session中没有用户名")
        return JsonResponse(res)
    userInstance = GetUser(username)
    if not userInstance:
        res = wrapTheJson("failed", "没有这个用户")
        return JsonResponse(res)
    userInstance.Types = ToTypeNum(types)
    userInstance.HasView = True
    userInstance.save()
    return JsonResponse(wrapTheJson("success",''))

# 根据收藏来获取某个类型的推荐
def GetRecByIds(movids,type,count):
    Recmovies=[]
    #获取推荐
    Recmovieids=GetRecommList(ids=movids,count=count,type=type)
    for recmovie in Recmovieids:
        Recmovies.append(GetFilm(recmovie))
    return Recmovies

#获取评论
def GetReply(request):
    movName=request.GET.get('movname','')
    movId=request.GET.get('movid','')
    startIdx=int(request.GET.get('start',0))
    count=int(request.GET.get('count',20))

    username = request.session.get('user1', '')
    userInstance = GetUser(username)
    if movId=='':
        movInss=Movie.objects.filter(MovName=movName)
        if not movInss.exists():
            res=wrapTheJson('failed','无法找到该电影')
            return JsonResponse(res)
        movIns=movInss[0]
        movId=movIns.MovId
    try:
        result=GetReplies(movId,userInstance)
    except Exception as e:
        res=wrapTheJson('failed',e.__str__())
        return JsonResponse(res)
    finally:
        data={}
        data['count']=len(result)
        if len(result)<=startIdx+count:
            data['replylist'] = result[startIdx:]
        else:
            data['replylist']=result[startIdx:startIdx+count]
        res=wrapTheJson('success','',data)
        return JsonResponse(res)

def getWrappedRecommand(ids,type,count,user):
    result=(wrapTheMovie(GetRecByIds(movids=ids,type=type,count=count)))
    if not result:
        result=wrapTheMovie(GetRecommByType(type,count,user))
    if len(result)<count:
        rest=count-len(result)
        temp=wrapTheMovie(GetRecommByType(type,rest,user))
        for t in temp:
            result.append(t)
    return result

def getRec(request):
    username = request.session.get("user1", '')
    print(username)
    if username == '':
        res = wrapTheJson("failed", "session中没有用户名")
        return JsonResponse(res)
    userInstance = GetUser(username)
    if not userInstance:
        res = wrapTheJson("failed", "没有这个用户")
        return JsonResponse(res)
    uid = userInstance.UserId
    print(userInstance.Types)
    allmovies = []
    comics = []
    crimes = []
    threats = []
    fictions = []
    jingsongs = []
    loves = []
    actions = []
    wests = []
    musics = []
    disasters = []
    xijvs = []
    jvqings = []
    if userInstance.HasView == True:
        #获取收藏记录
        favRecords = models.FavoriteRecord.objects.filter(UserId=uid).order_by("-RecordTime")
        movids = []
        for favRecord in favRecords:
            movids.append(favRecord.TargetId)
        if len(movids)>0:
            defaultAllType=~(1<<30)
            testP1 = GetRecByIds(movids=movids,type=defaultAllType,count=20)
            print("testP1",testP1.__len__())
            allmovies = getWrappedRecommand(movids,userInstance.Types,20,userInstance)

            comics = (getWrappedRecommand(ids=movids,type=(1<<2),count=20,user=userInstance))
            crimes=(getWrappedRecommand(ids=movids,type=(1<<4),count=20,user=userInstance))
            threats=(getWrappedRecommand(ids=movids,type=(1<<7),count=20,user=userInstance))
            fictions=(getWrappedRecommand(ids=movids,type=(1<<9),count=20,user=userInstance))
            jingsongs=getWrappedRecommand(ids=movids,type=(1<<10),count=20,user=userInstance)
            loves=getWrappedRecommand(ids=movids,type=(1<<11),count=20,user=userInstance)
            actions=getWrappedRecommand(ids=movids,type=(1<<15),count=20,user=userInstance)
            wests=getWrappedRecommand(ids=movids,type=(1<<18),count=20,user=userInstance)
            musics=getWrappedRecommand(ids=movids,type=(1<<12),count=20,user=userInstance)
            disasters=getWrappedRecommand(ids=movids,type=(1<<23),count=20,user=userInstance)
            jvqings=getWrappedRecommand(ids=movids,type=(1<<29),count=20,user=userInstance)

            data = {}
            data['movietypes'] = ['动画', '犯罪', '恐怖', '科幻', '惊悚', '爱情', '动作', '西部', '音乐', '灾难', '喜剧', '剧情']
            data['alltypemovie'] = allmovies
            data['动画'] = comics
            data['犯罪'] = crimes
            data['恐怖'] = threats
            data['科幻'] = fictions
            data['惊悚'] = jingsongs
            data['爱情'] = loves
            data['动作'] = actions
            data['西部'] = wests
            data['音乐'] = musics
            data['灾难'] = disasters
            data['剧情'] = jvqings
            res = wrapTheJson("success", '', data=data)
            return JsonResponse(res)

    comics = wrapTheMovie(GetRecommByType(1<<2,20,user=userInstance))
    crimes = wrapTheMovie(GetRecommByType(1<<4,20,user=userInstance))
    threats = wrapTheMovie(GetRecommByType(1<<7,20,user=userInstance))
    fictions = wrapTheMovie(GetRecommByType(1<<9,20,user=userInstance))
    jingsongs = wrapTheMovie(GetRecommByType(1<<10,20,user=userInstance))
    loves = wrapTheMovie(GetRecommByType(1<<11,20,user=userInstance))
    actions = wrapTheMovie(GetRecommByType(1<<15,20,user=userInstance))
    wests = wrapTheMovie(GetRecommByType(1<<18,20,user=userInstance))
    musics = wrapTheMovie(GetRecommByType(1<<12,20,user=userInstance))
    disasters = wrapTheMovie(GetRecommByType(1<<23,20,user=userInstance))
    jvqings = wrapTheMovie(GetRecommByType(1<<29,20,user=userInstance))
    allmovies=(wrapTheMovie(GetRecommByType(userInstance.Types,20,user=userInstance)))

    data = {}
    data['movietypes'] = ['动画', '犯罪', '恐怖', '科幻', '惊悚', '爱情', '动作', '西部', '音乐', '灾难', '喜剧', '剧情']
    data['alltypemovie'] = allmovies
    data['动画'] = comics
    data['犯罪'] = crimes
    data['恐怖'] = threats
    data['科幻'] = fictions
    data['惊悚'] = jingsongs
    data['爱情'] = loves
    data['动作'] = actions
    data['西部'] = wests
    data['音乐'] = musics
    data['灾难'] = disasters
    data['剧情'] = jvqings
    res = wrapTheJson("success", '', data=data)
    return JsonResponse(res)


# 创建评论
def createReply(request):
    recv_data = json.loads(request.body.decode())  # 解析前端发送的JSON格式的数据
    type = recv_data['type']
    content = recv_data['content']
    username = request.session.get('user1', '')
    userInstance = GetUser(username)
    AddUserExp(userInstance,10)
    uid = userInstance.UserId
    if(recv_data['type'] == "movie"):
        grade = recv_data['grade']
        movid= recv_data['movieid']
        reply=models.ReplyRecord.objects.create(UserId=userInstance, TargetId=movid, ReplyType=1, ReplyGrade=grade, ReplyContent=content)
        # reply = models.ReplyRecord.objects.filter(UserId=userInstance, TargetId=movid, ReplyType=1, ReplyGrade=grade, ReplyContent=content).order_by("-RecordTime")[0]

        result=GetReplies(movid,userInstance)
        print(reply)
        data = {}
        data['name'] = username
        data['content'] = content
        data['agree']=reply.AgreeCount
        data['score'] = grade
        data['time'] = reply.RecordTime
        data['replyid'] = reply.RecordId
        data['reply'] = []
        data['count']=len(result)
        res = wrapTheJson('success', '', data)
    else:
        print(type)
        replyid = recv_data['replyid']
        movid=recv_data['movieid']
        reply=models.ReplyRecord.objects.create(UserId=userInstance, TargetId=replyid, ReplyType=2, ReplyContent=content)
        targetRep=ReplyRecord.objects.get(RecordId=replyid)
        #reply = models.ReplyRecord.objects.filter(UserId=userInstance, TargetId=replyid, ReplyType=2, ReplyContent=content).order_by("-RecordTime")[0]
        print(reply)
        data = {}
        data['name'] = username
        data['content'] = content
        data['agree']=reply.AgreeCount
        data['time'] = reply.RecordTime
        data['replyid'] = reply.RecordId
        data['target']=targetRep.UserId.UserName
        data['reply'] = []
        data['count']=0
        res = wrapTheJson('success', '', data)
    return JsonResponse(res)