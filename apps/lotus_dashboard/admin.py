from django.contrib import admin

from lotus_dashboard.models import *


class DashboardColumnAdmin(admin.ModelAdmin):
    list_display = ['site', 'columns']
    list_filter = ['site']


class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip', 'description']
    list_filter = ['ip', 'description']


class CrmAccountAdmin(admin.ModelAdmin):
    list_display = ['crm_name', 'crm_url', 'sales_goal', 'paused', 'password_updated', 'rebill_length']


class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['name', 'type']


class LabelGoalAdmin(admin.ModelAdmin):
    list_display = ['crm', 'label', 'goal', 'visible']
    list_filter = ['crm', 'label', 'goal', 'visible']


class LabelCampaignAdmin(admin.ModelAdmin):
    list_display = ['crm', 'campaign_id', 'campaign_name', 'campaign_label']
    list_filter = ['crm']
    search_fields = ['campaign_id']
    readonly_fields = ['crm', 'campaign_id', 'campaign_name']


admin.site.register(DashboardColumn, DashboardColumnAdmin)
admin.site.register(BlockedIP, BlockedIPAdmin)
admin.site.register(CrmAccount, CrmAccountAdmin)
admin.site.register(CrmToken)
admin.site.register(CrmResult)
admin.site.register(Label, LabelAdmin)
admin.site.register(LabelGoal, LabelGoalAdmin)
admin.site.register(LabelCampaign, LabelCampaignAdmin)
