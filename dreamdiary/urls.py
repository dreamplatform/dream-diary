
#coding=utf-8

from django.conf.urls.defaults import *


urlpatterns = patterns('dreamdiary.views',
    #common
    url(r'^$', 'index', name='diary_index'),
    url(r'^ajax/listsnippet/$', 'ajax_paginated_snippet', name='ajax_paginated_snippet'),
    url(r'^ajax/color/$', 'ajax_color', name='ajax_color'),
    url(r'^ajax/order/$', 'ajax_order', name='ajax_order'),
    url(r'^network/(?P<network_id>\d+)/(?P<user_id>\d+)?', 'network', name='network'),
    url(r'^archive/$', 'archive', name='archive'),

    #supervisor
    url(r'^network/edit/(?P<network_id>\d+)?', 'supervisor_edit_network', name='supervisor_edit_network'),
    url(r'^network/share/(?P<network_id>\d+)/', 'supervisor_share_network', name='supervisor_share_network'),
    url(r'^task/edit/(?P<task_id>\d+)?', 'supervisor_edit_task', name='supervisor_edit_task'),

    #user
    url(r'work/edit/(?P<work_id>\d+)?', 'user_edit_work', name='user_edit_work'),
    url(r'ajax/answer/', 'user_ajax_answer', name='user_ajax_answer'),

)

