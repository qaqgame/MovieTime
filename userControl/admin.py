from django.contrib import admin
from userControl.models import User,UserManager
# Register your models here.
admin.register([User, UserManager])