from django.shortcuts import render, redirect
from Main import models
from django.http import JsonResponse
import json
# Create your views here.

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




