from django.conf.urls import url
from lotus_dashboard import views


urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^initial_report/$', views.view_initial_report, name='report_initial'),
    url(r'^rebill_report/$', views.view_rebill_report, name='report_rebill'),
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
    url(r'^ajax_initial_list/$', views.ajax_initial_list, name='url_initial_list'),
    url(r'^ajax_rebill_list/$', views.ajax_rebill_list, name='url_rebill_list'),

    url(r'^get_dashboard_sales/$', views.view_get_dashboard_sales),
    url(r'^update_campaigns/$', views.view_update_campaigns),
    url(r'^get_initial_reports/$', views.view_get_initial_reports),
    url(r'^get_rebill_reports/$', views.view_get_rebill_reports),
]
