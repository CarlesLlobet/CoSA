from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.sqlmap_new, name='sqlmap_new'),
    url(r'how_to/$', views.sqlmap_howto, name='sqlmap_how_to'),
    url(r'tasks/$', views.sqlmap_tasks, name='sqlmap_tasks'),
    url(r'task/(?P<id>[0-9]+)/$', views.sqlmap_task, name='sqlmap_task'),
    url(r'delete/(?P<id>[0-9]+)/$', views.sqlmap_delete, name='sqlmap_delete'),
    url(r'relaunch/(?P<id>[0-9]+)/$', views.sqlmap_relaunch, name='sqlmap_relaunch'),
    url(r'modify/(?P<id>[0-9]+)/$', views.sqlmap_modify, name='sqlmap_modify'),
    url(r'download/(?P<id>[0-9]+)/$', views.sqlmap_download, name='sqlmap_download'),
]