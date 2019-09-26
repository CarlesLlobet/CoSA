from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from API import views

urlpatterns = [
    url(r'^OpenVAS/get_state/(?P<id>[0-9]+)/$', views.OpenVAS_getState),
    url(r'^OpenVAS/kill/(?P<id>[0-9]+)/$', views.OpenVAS_kill),
    url(r'^OpenVAS/add_result/(?P<id>[0-9]+)/$', views.OpenVAS_addResult.as_view()),
    url(r'^OpenVAS/set_state/(?P<id>[0-9]+)/$', views.OpenVAS_setState.as_view()),
    url(r'^OpenVAS/set_report/(?P<id>[0-9]+)/$', views.OpenVAS_setReport.as_view()),
    url(r'^OpenVAS/set_percentage/(?P<id>[0-9]+)/$', views.OpenVAS_setPercentage.as_view()),
    url(r'^OpenVAS/get_next/$', views.OpenVAS_getNext),
    url(r'^OpenVAS/get_deleted/$', views.OpenVAS_getDeleted),
    # url(r'^SQLmap/add_results/(?P<id>[0-9]+)/$', views.SQLmap_addResult.as_view()),
    # url(r'^SQLmap/add_report/(?P<id>[0-9]+)/$', views.SQLmap_setReport.as_view()),
    # url(r'^SQLmap/set_state/(?P<id>[0-9]+)/$', views.SQLmap_setState.as_view()),
    # url(r'^SQLmap/get_next/$', views.SQLmap_getNext),
    # url(r'^SQLmap/get_state/(?P<id>[0-9]+)/$', views.SQLmap_getState),
    # url(r'^SQLmap/kill/(?P<id>[0-9]+)/$', views.SQLmap_kill),
    # url(r'^w3af/add_results/(?P<id>[0-9]+)/$', views.w3af_addResult.as_view()),
    # url(r'^w3af/add_report/(?P<id>[0-9]+)/$', views.w3af_setReport.as_view()),
    # url(r'^w3af/set_state/(?P<id>[0-9]+)/$', views.w3af_setState.as_view()),
    # url(r'^w3af/get_next/$', views.w3af_getNext),
    # url(r'^w3af/get_state/(?P<id>[0-9]+)/$', views.w3af_getState),
    # url(r'^w3af/kill/(?P<id>[0-9]+)/$', views.w3af_kill),
]

urlpatterns = format_suffix_patterns(urlpatterns)