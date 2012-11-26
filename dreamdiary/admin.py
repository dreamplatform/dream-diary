
#encoding=utf-8

from django.contrib import admin
from dreamdiary.models import *

admin.site.register(UserGroup)

admin.site.register(Network)
admin.site.register(Task)
admin.site.register(Work)
admin.site.register(TaskAttachment)
admin.site.register(WorkAttachment)

admin.site.register(Connection)
admin.site.register(Answer)
admin.site.register(Color)
