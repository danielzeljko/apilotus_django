from django.conf.urls import url, include

from rest_framework import routers

from lotus_dashboard import views, ajax_apis
from lotus_dashboard.viewsets import *

app_name = 'lotus_dashboard'
router = routers.DefaultRouter()
router.register(r'dashboard_column', DashboardColumnViewSet)
router.register(r'cap_update_result', CapUpdateResultViewSet)
router.register(r'offer', OfferViewSet)
router.register(r'affiliate', AffiliateViewSet)
router.register(r'billing_affiliate', BillingAffiliateViewSet)

urlpatterns = [
    url('^api/', include(router.urls)),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^initial_report/$', views.view_initial_report, name='report_initial'),
    url(r'^rebill_report/$', views.view_rebill_report, name='report_rebill'),
    # url(r'^dashboard/$', views.dashboard, name='setting_campaign'),
    url(r'^cap_update/$', views.view_cap_update, name='cap_update'),
    url(r'^affiliates/$', views.view_affiliates, name='affiliates'),
    url(r'^billing/$', views.view_billing_dashboard, name='billing_dashboard'),
    url(r'^billing_report/$', views.view_billing_report, name='billing_reports'),
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

    url(r'^export_billing_report/$', view=views.export_billing_report),

    # ajax requests in ajax_apis
    url(r'^ajax_add_affiliate/$', ajax_apis.ajax_add_affiliate),
    url(r'^ajax_edit_affiliate/$', ajax_apis.ajax_edit_affiliate),
    url(r'^ajax_delete_affiliate/$', ajax_apis.ajax_delete_affiliate),
    url(r'^ajax_affiliate_special_code/$', ajax_apis.ajax_affiliate_special_code),

    # ajax requests in viewsets
    url(r'^ajax_cap_update_list/$', view=CapUpdateList.as_view(), name='url_cap_update_list'),
    url(r'^ajax_billing_list/$', view=BillingList.as_view(), name='url_billing_list'),
    url(r'^ajax_billing_result_list/$', view=BillingResultList.as_view(), name='url_billing_result_list'),
    url(r'^ajax_affiliation_list/$', view=AffiliationList.as_view(), name='url_affiliation_list'),

    # tasks
    url(r'^get_dashboard_sales/$', views.view_get_dashboard_sales),
    url(r'^update_campaigns/$', views.view_update_campaigns),
    url(r'^get_initial_reports/$', views.view_get_initial_reports),
    url(r'^get_rebill_reports/$', views.view_get_rebill_reports),
    url(r'^get_cap_update_result/$', views.view_get_cap_update_result),
    url(r'^get_billing_result/$', views.view_billing_result),
]
