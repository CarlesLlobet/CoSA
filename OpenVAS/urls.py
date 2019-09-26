"""AAPT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from OpenVAS import views

urlpatterns = [
    url(r'^$', views.openvas_new, name='openvas_new'),
    url(r'tasks/$', views.openvas_tasks, name='openvas_tasks'),
    url(r'how_to/$', views.openvas_howto, name='openvas_howto'),
    url(r'task/(?P<id>[0-9]+)/$', views.openvas_task, name='openvas_task'),
    url(r'delete/(?P<id>[0-9]+)/$', views.openvas_delete, name='openvas_delete'),
    url(r'modify/(?P<id>[0-9]+)/$', views.openvas_modify, name='openvas_modify'),
    url(r'download/(?P<id>[0-9]+)/$', views.openvas_download, name='openvas_download'),
    url(r'relaunch/(?P<id>[0-9]+)/$', views.openvas_relaunch, name='openvas_relaunch'),
]
