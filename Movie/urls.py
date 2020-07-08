"""Movie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from userControl.views import signup, ShowMoviePage, getRec
from userControl.views import login
from userControl.views import UserSpace
from userControl.views import timeLine
from userControl.views import keep
from userControl.views import ViewRecord
from userControl.views import movInfo
from userControl.views import getKeep
from userControl.views import search
from userControl.views import index
from userControl.views import createReply
from userControl.views import GetReply
from userControl.views import agree
from userControl.views import cancelAgree
from userControl.views import getUser
from userControl.views import logout
from userControl.views import likeType

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sign-up/', signup),
    path('login/', login),
    path('showmovie/',ShowMoviePage),
    path('showmovie/search',search),
    re_path(r'^user/(\w+)$', UserSpace),
    re_path(r'^user/(\w+)/timeline$', timeLine),
    path('keepMovie', keep),
    re_path(r'^user/(\w+)/historyrecord$', ViewRecord),
    re_path(r'^movie/(\w+)$', movInfo),
    re_path(r'user/(\w+)/keep', getKeep),
    path('index/',index),
    path('recom/',getRec),
    path('createreply/',createReply),
    path('getreply',GetReply),
    path('agree',agree),
    path('cancelagree',cancelAgree),
    path('loginVerify/',getUser),
    path('logout/',logout),
    path('liketype/',likeType)
]
