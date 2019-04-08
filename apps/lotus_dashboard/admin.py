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
    list_filter = ['crm', 'campaign_id']
    search_fields = ['campaign_id']
    readonly_fields = ['crm', 'campaign_id', 'campaign_name']


class OfferAdmin(admin.ModelAdmin):
    list_display = ['crm', 'name', 'label', 'type', 's1_payout', 's2_payout']
    list_filter = ['crm', 'label']
    raw_id_fields = ['step1', 'step2', 'step1_prepaids', 'step2_prepaids', 'step1_tablet', 'step2_tablet']


class AffiliateAdmin(admin.ModelAdmin):
    list_display = ['name', 'afid', 'code', 'bot']


class AffiliateOfferAdmin(admin.ModelAdmin):
    list_display = ['affiliate', 'offer', 'goal', 's1_payout', 's2_payout']
    list_filter = ['affiliate', 'offer']


class RebillAdmin(admin.ModelAdmin):
    list_display = ['crm']
    raw_id_fields = ['rebills']


admin.site.register(DashboardColumn, DashboardColumnAdmin)
admin.site.register(BlockedIP, BlockedIPAdmin)
admin.site.register(CrmAccount, CrmAccountAdmin)
admin.site.register(CrmToken)
admin.site.register(CrmResult)
admin.site.register(Label, LabelAdmin)
admin.site.register(LabelGoal, LabelGoalAdmin)
admin.site.register(LabelCampaign, LabelCampaignAdmin)

admin.site.register(OfferLabel)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Affiliate, AffiliateAdmin)
admin.site.register(AffiliateOffer, AffiliateOfferAdmin)

admin.site.register(InitialResult)
admin.site.register(Rebill, RebillAdmin)
