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
from Main.models import Movie, IDCount, Actor, MovieTag, CosRelation, FavoriteRecord, ViewRecord
Movie.objects.all().delete()
Actor.objects.all().delete()
MovieTag.objects.all().delete()
IDCount.objects.all().delete()
CosRelation.objects.all().delete()
FavoriteRecord.objects.all().delete()
ViewRecord.objects.all().delete()
