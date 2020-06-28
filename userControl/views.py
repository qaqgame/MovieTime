from django.shortcuts import render, redirect
from Main import models
from django.http import JsonResponse
# Create your views here.

def login(request):
    if request.method == 'GET':
        path = request.GET.get('next', '')
    if request.method == 'POST':
        conditions = {
            'UserName': request.POST['name'],
            'UserPsw':  request.POST['password'],
        }
        user = models.User.objects.filter(**conditions)
        if user:
            name = request.POST['name']
            # ret = redirect("/index/")
            request.session['is_login'] = True
            request.session['user1'] = name
            path = request.POST.get('next')
            path = '/' + path
            return redirect(path)
        else:
            return JsonResponse({"password": "false"})


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
        conditions = {
            'UserName': request.POST['name'],
        }
        res = models.User.objects.filter(**conditions)
        if res:
            return JsonResponse({'error': '账号存在'})
        else:
            user = models.User.objects.create(UserName=request.POST['name'],
                                              UserPwd=request.POST['password'],
                                              )
            print(user, type(user))
            return  JsonResponse({'signup': 'success'})
    return render(request, "signup.html")




