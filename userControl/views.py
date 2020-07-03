from django.shortcuts import render, redirect
from Main import models
from django.http import JsonResponse
import json
# Create your views here.
from Main.utils import MsgTemplate


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
            name = recv_data['name']         #todo-是否传这个
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
    return redirect('/session_login/')


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
            return JsonResponse({'error': '账号存在', 'result': 'failed', 'reason': '帐号存在', 'formtype': 'register'})
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

