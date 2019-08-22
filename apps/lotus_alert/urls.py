from django.conf.urls import url, include

from rest_framework import routers

from lotus_alert import views
from lotus_alert.viewsets import *

app_name = 'lotus_alert'
router = routers.DefaultRouter()
router.register(r'alert_type', AlertTypeViewSet)
router.register(r'alert_status', AlertStatusViewSet)

urlpatterns = [
    url('^api/', include(router.urls)),

    url(r'^ajax_setting_alert_list_by_cid/$', views.view_setting_alert_list_by_cid, name='url_setting_alert_list_by_cid'),
    url(r'^ajax_setting_alert_edit/$', views.view_setting_alert_edit, name='url_setting_alert_edit'),
    url(r'^ajax_alert_recent_list/$', views.view_alert_recent_list, name='url_alert_recent_list'),
    url(r'^ajax_alert_delete/$', views.view_alert_delete, name='url_ajax_alert_delete'),
    url(r'^ajax_alert_delete_all/$', views.view_alert_delete_all, name='url_alert_delete_all'),
]
