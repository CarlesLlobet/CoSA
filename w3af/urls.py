from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.w3af_new, name='w3af_new'),
    url(r'how_to/$', views.w3af_howto, name='w3af_howto'),
    url(r'tasks/$', views.w3af_tasks, name='w3af_tasks'),
    url(r'task/(?P<id>[0-9]+)/$', views.w3af_task, name='w3af_task'),
    url(r'delete/(?P<id>[0-9]+)/$', views.w3af_delete, name='w3af_delete'),
    url(r'relaunch/(?P<id>[0-9]+)/$', views.w3af_relaunch, name='w3af_relaunch'),
    url(r'modify/(?P<id>[0-9]+)/$', views.w3af_modify, name='w3af_modify'),
    url(r'download/(?P<id>[0-9]+)/$', views.w3af_download, name='w3af_download'),
]