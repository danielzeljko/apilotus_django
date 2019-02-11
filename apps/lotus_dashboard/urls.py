from django.conf.urls import url
from lotus_dashboard import views


urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    url(r'^ajax_dashboard_columns_get/$', views.view_dashboard_columns_get, name='url_dashboard_columns_get'),
    url(r'^ajax_crm_list/$', views.view_crm_list, name='url_crm_list'),
]
