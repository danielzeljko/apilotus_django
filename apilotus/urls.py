"""APILotus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView

from apilotus import settings
from apps.lotus_auth import *


urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),

    url(settings.LOTUS_ADMIN_URL, admin.site.urls),

    url(r'^rosetta/', include('rosetta.urls')),

    path('i18n/', include('django.conf.urls.i18n')),

    url(r'^accounts/', include('lotus_auth.urls')),
    url(r'^admin/', include('lotus_dashboard.urls')),
    url(r'^alert/', include('lotus_alert.urls')),

    url(r'^$', RedirectView.as_view(url='accounts/login', permanent=False)),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^bot/', include('django_telegrambot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
