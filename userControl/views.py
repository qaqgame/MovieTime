from django.shortcuts import render, redirect
from Main.models import *
from Main import models
from django.http import JsonResponse
import json
# Create your views here.
from Main.utils import MsgTemplate, GetMovImgUrl
from Main.utils import GetFilm, wrapTheJson, GetUser, GetTitle, wrapTheDetail

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
            request.session['is_login'] = True
            request.session['user1'] = name
            # path = request.POST.get('next')
            # path = '/' + path
            # return redirect(path)
            return JsonResponse({"username": name, "result": "success", "reason": "登录成功", "formtype": "login"})
        else:
            return JsonResponse({"password": "false", "result": "failed", "reason": "用户名或密码错误", "formtype": "login"})


def logout(request):
    request.session.flush()
    return redirect('/login/')


def index(request):
    status = request.session.get('is_login')
    if not status:
        return JsonResponse({'hasSes': 'false', 'next': '/ses_index/'})
    else:
        return render(request, 's_index.html')


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
        userData={'username':username,'currlevel':userlv,'currexp':usercur,'maxexp':usermax}

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
                cover='/static/cover/default_cover.bmp'
            else:
                ext=imgPath.split('.').pop()
                movId=MovInstance.MovId
                filename = 'Cover_{0}.{1}'.format(movId, ext)
                cover='/static/cover/'+movId+'/'+filename

            # 获取电影名
            name=MovInstance.MovName
            favResultList.append({'movieimgurl': cover, 'moviename': name, 'extrainfo': date})


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
            movList.append(oneMessage)
        movList.sort(key=lambda w:w["extrainfo"])
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
    movName = mn
    print(movName)
    movInstance = models.Movie.objects.filter(MovName=movName)
    if not movInstance.exists():
        res = wrapTheJson("failed", '不存在这部电影')
        return JsonResponse(res)
    movInstance = movInstance[0]
    data = {}
    movieinfo = {}
    movieinfo['name'] = movInstance.MovName
    movieinfo['type'] = movInstance.MovType
    movieinfo['time'] = movInstance.MovDate
    movieinfo['director'] = movInstance.MovDirector
    movieinfo['lastfor'] = movInstance.MovLength
    # 改模型
    movieinfo['lang'] = movInstance.MovLanguage
    movieinfo['coverurl'] = GetMovImgUrl(movInstance)
    movieinfo['description'] = movInstance.MovDescription

    actorIds = models.ActorConnection.objects.filter(MovId=movInstance.MovId)
    actors = []
    print(actorIds[0].ActorId, actorIds[0])
    for id in actorIds:
        print(id.ActorId)

        actor = id.ActorId.ActorName
        actors.append(actor)
    movieinfo['actors'] = actors

    # 评分
    # movieinfo['rate'] = movInstance.MovRate
    uname = GetUser(request.session.get('user1'))
    if not uname:
        ifKeeped = 'false'
    else:
        uid = GetUser(uname)
        fav = models.FavoriteRecord.objects.filter(UserId=uid, TargetId=movieinfo.MovId);
        if not fav:
            ifKeeped = 'false'
        else:
            ifKeeped = 'true'
    movieinfo['ifKeeped'] = ifKeeped

    data['movieinfo'] = movieinfo
    res = wrapTheJson("success", '', data=data)
    return JsonResponse(res)


# 时间线
def timeLine(request, un):
    uid = GetUser(un).UserId
    timelines = []
    for sub in models.BaseRecord.__subclasses__():
        timeline = {}
        messages = sub.objects.filter(UserId=uid)
        if not messages.exists():
            continue
        for message in messages:
            timeline['actiontime'] = message.RecordTime
            timeline['title'] = GetTitle(sub.__name__)
            timeline['detail'] = wrapTheDetail(sub.__name__, message.TargetId)
            timelines.append(timeline)
    timelines.sort(key=lambda w:w["actiontime"])
    data = {}
    data['timeline'] = timelines
    res = wrapTheJson("success", "", data=data)
    return JsonResponse(res)


# 搜索
def search(request):
    type = request.GET.get('type', '')
    field = request.GET.get('field', '')
    time = request.GET.get('time', '')
    moviename = request.GET.get('moviename', '')
    conditions = {}
    if type != '':
        conditions['MovType'] = type
    if field != '':
        conditions['MovOrigin'] = field
    if time != '':
        conditions['MovDate'] = time
    if moviename != '':
        conditions['MovName'] = moviename
    movies = models.Movie.objects.filter(**conditions)
    if not movies.exists():
        res = wrapTheJson("failed", "没有符合条件的电影")
        return JsonResponse(res)
    data = {}
    allmovies = []
    for movie in movies:
        info = {}
        info['movieimgurl'] = GetMovImgUrl(movie)
        info['moviename'] = movie.MovName
        # 需要修改
        info['extrainfo'] = movie.MovRate
        allmovies.append(info)
    data['allmovies'] = allmovies
    res = wrapTheJson("success", "", data=data)
    return JsonResponse(res)


def keep(request):
    moviename = request.GET.get("moviename", '')
    if moviename == '':
        res = wrapTheJson("failed", "没有得到电影名")
        return JsonResponse(res)
    movie = models.Movie.objects.filter(MovName=moviename)
    if not movie.exists():
        res = wrapTheJson("failed", "没有该电影名的数据")
        return JsonResponse(res)
    movId = movie[0].MovId
    uid = GetUser(request.session['user1']).UserId
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
        if not movie.exists():
            continue
        message['movieimgurl'] = GetMovImgUrl(movie)
        message['moviename'] = movie.MovName
        message['extrainfo'] = favMovie.RecordTime
        timeline.append(message)
    data['keepmovies'] = timeline
    res = wrapTheJson("success", '', data)
    return JsonResponse(res)
