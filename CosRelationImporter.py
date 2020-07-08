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
from Recom.Utils import ImportRelation

import numpy as np

movies_index = np.loadtxt('movies_index.csv', dtype = np.int, delimiter=',')

ids_r = np.loadtxt('ids.csv',dtype = np.int,delimiter=',')
distances_r = np.loadtxt('distances.csv',dtype = np.float32,delimiter=',')
ids = ids_r.reshape(21113, 30)
distances = distances_r.reshape(21113, 30)

dic = np.load('movies_dic.npy', allow_pickle=True).item()

# change from 21113 to 2000
for i in range(21113):
    for j in range(30):
        # print(i, " ", j, " ", movies_index[i], " ", ids[i][j])
        if movies_index[ids[i][j]] in dic.keys():
            if movies_index[i] in dic.keys():
                ImportRelation(dic[movies_index[i]], movies_index[i], dic[movies_index[ids[i][j]]], ids[i][j], distances[i][j])
print('all finished')
