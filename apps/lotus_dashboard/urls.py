from django.conf.urls import url
from lotus_dashboard import views


urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='report_initial'),
    url(r'^dashboard/$', views.dashboard, name='report_rebill'),
    url(r'^dashboard/$', views.dashboard, name='setting_crm'),
    url(r'^dashboard/$', views.dashboard, name='setting_campaign'),
    url(r'^dashboard/$', views.dashboard, name='setting_alert'),
    url(r'^dashboard/$', views.dashboard, name='setting_accounts'),
    url(r'^dashboard/$', views.dashboard, name='cap_update'),
    url(r'^dashboard/$', views.dashboard, name='cap_offers'),
    url(r'^dashboard/$', views.dashboard, name='cap_affiliates'),
    url(r'^dashboard/$', views.dashboard, name='billing_dashboard'),
    url(r'^dashboard/$', views.dashboard, name='billing_offers'),
    url(r'^dashboard/$', views.dashboard, name='billing_affiliates'),
    url(r'^dashboard/$', views.dashboard, name='billing_reports'),
    url(r'^dashboard/$', views.dashboard, name='setting_payment'),
    url(r'^dashboard/$', views.dashboard, name='logout'),

    url(r'^ajax_dashboard_columns_get/$', views.view_dashboard_columns_get, name='url_dashboard_columns_get'),
    url(r'^ajax_crm_list/$', views.view_crm_list, name='url_crm_list'),
    url(r'^ajax_dashboard_sales_all/$', views.view_dashboard_sales_all, name='url_dashboard_sales_all'),
    url(r'^ajax_setting_crm_goal/$', views.view_setting_crm_goal, name='url_setting_crm_goal'),
    url(r'^ajax_setting_crm_edit/$', views.view_setting_crm_edit, name='url_setting_crm_edit'),
    url(r'^ajax_crm_position_set/$', views.view_crm_position_set, name='url_ajax_crm_position_set'),

    url(r'^get_dashboard_sales/$', views.view_get_dashboard_sales),
]
