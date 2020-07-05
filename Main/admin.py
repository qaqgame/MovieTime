from django.contrib import admin
from Main.models import *
# Register your models here.
admin.site.register(Movie)
admin.site.register(MovieTag)
admin.site.register(User)
admin.site.register(Agree)
admin.site.register(Actor)
admin.site.register(ReplyRecord)
admin.site.register(IDCount)
admin.site.register(MovTagConnection)
admin.site.register(ActorConnection)
admin.site.register(FavoriteRecord)
admin.site.register(ViewRecord)
admin.site.register(CosRelation)