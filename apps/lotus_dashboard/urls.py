from django.conf.urls import url
from lotus_dashboard import views


urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='report_initial'),
    url(r'^dashboard/$', views.dashboard, name='report_rebill'),
    url(r'^dashboard/$', views.dashboard, name='setting_campaign'),
    url(r'^dashboard/$', views.dashboard, name='cap_update'),
    url(r'^dashboard/$', views.dashboard, name='cap_offers'),
    url(r'^dashboard/$', views.dashboard, name='cap_affiliates'),
    url(r'^dashboard/$', views.dashboard, name='billing_dashboard'),
    url(r'^dashboard/$', views.dashboard, name='billing_offers'),
    url(r'^dashboard/$', views.dashboard, name='billing_affiliates'),
    url(r'^dashboard/$', views.dashboard, name='billing_reports'),
    url(r'^dashboard/$', views.dashboard, name='setting_payment'),
    url(r'^dashboard/$', views.dashboard, name='logout'),

    url(r'^ajax_dashboard_columns_get/$', views.ajax_dashboard_columns_get, name='url_dashboard_columns_get'),

    url(r'^ajax_crm_list/$', views.ajax_crm_list, name='url_crm_list'),
    url(r'^ajax_setting_crm_list/$', views.ajax_setting_crm_list, name='url_setting_crm_list'),
    url(r'^ajax_setting_crm_add/$', views.ajax_setting_crm_add, name='url_setting_crm_add'),
    url(r'^ajax_setting_crm_edit/$', views.ajax_setting_crm_edit, name='url_setting_crm_edit'),
    url(r'^ajax_setting_crm_delete/$', views.ajax_setting_crm_delete, name='url_setting_crm_delete'),
    url(r'^ajax_setting_crm_goal/$', views.ajax_setting_crm_goal, name='url_setting_crm_goal'),
    url(r'^ajax_crm_position_set/$', views.ajax_crm_position_set, name='url_crm_position_set'),

    url(r'^ajax_dashboard_sales_all/$', views.ajax_dashboard_sales_all, name='url_dashboard_sales_all'),
    url(r'^get_dashboard_sales/$', views.ajax_get_dashboard_sales),


    url(r'^update_campaigns/$', views.view_update_campaigns),
]
