from Main.models import *

# 导入电影
def ImportMovie(title,typeList,length,origin,company,director,content,tagList,cover=None):
    # 获取最终的类型
    temp=1
    finalType=0
    for type in typeList:
        finalType=finalType | (temp<<type)


    instance=Movie.objects.create(MovName=title,MovLength=length,MovOrigin=origin,MovType=finalType,MovCompany=company,
                         MovDirector=director, MovDescription=content)
    # 处理封面
    if cover !=None:
        instance.MovImg=cover

    # 保存电影
    instance.save()

    movId=Movie.objects.get(MovName=title).MovId

    # 处理tag
    for tag in tagList:
        # 查询tag
        queryResult=MovieTag.objects.get(MovTagCnt=tag)
        # 如果为空则先添加该tag
        if queryResult.exists():
            tagInstance=MovieTag.objects.create(MovTagCnt=tag)
            tagInstance.save()
            queryResult=MovieTag.objects.get(MovTagCnt=tag)
        # 获取tag的id
        realTagId=queryResult.MovTagId

        # 添加MovTagConnection
        connInstance=MovTagConnection.objects.create(MovId=movId,MovTagId=realTagId)
        connInstance.save()
