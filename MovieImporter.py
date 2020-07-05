# 独立使用django的model
import datetime
import sys
import os
from io import BytesIO
from urllib.request import urlopen

from django.core.files import File

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
# 找到根目录（与工程名一样的文件夹）下的settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie.settings')

import django

django.setup()

import csv
from Main.utils import ImportMovie

def GetList(items):
    result=[]
    tempList=str(items)
    if '/' in tempList:
        tempList=tempList.split('/')
        for i in tempList:
            i = i.strip()
            if i:
                result.append(i)
    else:
        result.append(tempList)
    return result

def GetSingle(items):
    temp=str(items)
    if '/' in temp:
        return temp.split('/')[0]
    return items

with open('movies.csv', 'r',encoding='UTF-8') as f:
    reader=csv.reader(f)
    if len(sys.argv)>1:
        starter=int(sys.argv[1])
    else:
        starter=1
    for i in range(0,starter):
        next(reader)
    for row in reader:
        originId=row[0]
        name=row[1]
        actors=row[3]
        cover=row[4]
        director=row[5]
        score=row[6]
        types=row[8]
        IMDB=row[9]
        length=row[11]
        regions=row[13]
        date=row[18]
        des=row[16]
        tags=row[17]
        lan=row[10]

        actorList=tagList=None
        if actors:
            actorList=GetList(actors)
        typeList=GetList(types)
        regionList=GetList(regions)
        if tags:
            tagList=GetList(tags)

        realDirector=GetSingle(director)

        if date and date!='0':
            tempDate=datetime.datetime.strptime(str(date),"%Y")
            realDate=tempDate.date()
        else:
            realDate=datetime.date.min

        if not lan:
            lan='未知'

        if not score:
            score=0

        if IMDB:
            temp=''.join(list(filter(str.isdigit,IMDB)))
            IMDB=int(temp)

        ImportMovie(title=name,typeList=typeList,length=length,origin=regionList,company=None,director=realDirector,
                    content=des,tagList=tagList,actorList=actorList,time=realDate,imdb=IMDB,tmdb=0,originId=originId,language=lan,cover=cover,score=score)
    print('all finished')