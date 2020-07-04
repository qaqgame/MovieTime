# 独立使用django的model
import datetime
import sys
import os
from io import BytesIO
from urllib.request import urlopen

from django.core.files import File

from Main.models import Movie, IDCount, Actor, MovieTag

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
# 找到根目录（与工程名一样的文件夹）下的settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie.settings')

import django

django.setup()

Movie.objects.all().remove()
Actor.objects.all().remove()
MovieTag.objects.all().remove()
IDCount.objects.all().remove()
