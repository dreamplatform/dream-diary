
#encoding=utf-8

from dreamdiary import settings as SETTINGS

def settings(request):
    return {
        u'DESKTOP_DOMAIN' : SETTINGS.DESKTOP_DOMAIN,
    }
