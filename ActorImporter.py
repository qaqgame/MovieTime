# 独立使用django的model
import sys
import os

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
# 找到根目录（与工程名一样的文件夹）下的settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie.settings')

import django

django.setup()

import csv
from Main.utils import ImportActor

with open('person.csv', 'r',encoding='UTF-8') as f:
    reader=csv.reader(f)

    for row in reader:
        profession=row[8]
        if '演员' in profession:
            name=row[1]
            sex=row[2]
            area=row[6]
            if not area:
                area='未知'
            ImportActor(name,sex,area)
    print('all finished')