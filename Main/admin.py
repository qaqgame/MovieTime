from django.contrib import admin
from Main.models import *
# Register your models here.
admin.site.register(Movie)
admin.site.register(MovieTag)
admin.site.register(User)
admin.site.register(Agree)
admin.site.register(ReplyRecord)