from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.NotificationListView.as_view(), name='notifications_list'),
    url(r'^mark-as-read/$', views.mark_read, name='notifications_mark_read'),
    url(r'^mark-as-read/(?P<id_lte>\d+)/$', views.mark_read, name='notifications_mark_read'),
    url(r'^(?P<pk>\d+)/$', views.goto, name='notification_link'),
    url(r'^delete/(?P<pk>\d+)/$', views.delete_notification, name='notification_delete'),
]
