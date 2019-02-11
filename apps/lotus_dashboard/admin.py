from django.contrib import admin

from lotus_dashboard.models import *


class DashboardColumnAdmin(admin.ModelAdmin):
    list_filter = ['site']
    list_display = ['site', 'columns']


class CrmAccountAdmin(admin.ModelAdmin):
    list_display = ['crm_name', 'crm_url', 'sales_goal', 'paused']


admin.site.register(DashboardColumn, DashboardColumnAdmin)
admin.site.register(CrmAccount, CrmAccountAdmin)
