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

from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from AAPT import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^', include('Core.urls')),
    url(r'^API/', include('API.urls')),
    url(r'^OpenVAS/', include('OpenVAS.urls')),
    url(r'^SQLmap/', include('SQLmap.urls')),
    url(r'^w3af/', include('w3af.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
