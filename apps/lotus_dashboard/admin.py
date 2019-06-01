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
    list_display = ['crm', 'campaign_id', 'campaign_name', 'campaign_label', 'updated_at']
    list_filter = ['updated_at', 'campaign_id', 'crm']
    search_fields = ['campaign_id', 'campaign_name']
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


class OfferBillingAdmin(admin.ModelAdmin):
    list_display = ['crm', 'name', 'label', 'desktop_trial', 'mobile_trial', 'desktop_mc', 'mobile_mc']
    raw_id_fields = ['trial_desktop', 'trial_mobile', 'mc_desktop', 'mc_mobile']

    def crm(self, obj):
        return obj.offer.crm.crm_name

    def name(self, obj):
        return obj.offer.name

    def label(self, obj):
        return obj.offer.label

    def desktop_trial(self, obj):
        return str(obj.trial_desktop.campaign_id) + ' - ' + obj.trial_desktop.crm.crm_name

    def mobile_trial(self, obj):
        return str(obj.trial_mobile.campaign_id) + ' - ' + obj.trial_mobile.crm.crm_name

    def desktop_mc(self, obj):
        return str(obj.mc_desktop.campaign_id) + ' - ' + obj.mc_desktop.crm.crm_name

    def mobile_mc(self, obj):
        return str(obj.mc_mobile.campaign_id) + ' - ' + obj.mc_mobile.crm.crm_name


class BillingAffiliateAdmin(admin.ModelAdmin):
    list_display = ['name', 'afid']


admin.site.register(DashboardColumn, DashboardColumnAdmin)
admin.site.register(BlockedIP, BlockedIPAdmin)
admin.site.register(CrmAccount, CrmAccountAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(LabelGoal, LabelGoalAdmin)
admin.site.register(LabelCampaign, LabelCampaignAdmin)

admin.site.register(OfferLabel)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Affiliate, AffiliateAdmin)
admin.site.register(AffiliateOffer, AffiliateOfferAdmin)

admin.site.register(Rebill, RebillAdmin)

admin.site.register(OfferBilling, OfferBillingAdmin)
admin.site.register(BillingAffiliate, BillingAffiliateAdmin)
