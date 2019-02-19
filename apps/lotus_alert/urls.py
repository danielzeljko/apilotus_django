from django.conf.urls import url
from lotus_alert import views


urlpatterns = [
    url(r'^ajax_setting_alert_list_by_cid/$', views.view_setting_alert_list_by_cid, name='url_setting_alert_list_by_cid'),
    url(r'^ajax_setting_alert_edit/$', views.view_setting_alert_edit, name='url_setting_alert_edit'),
]
