from django.utils import timezone

from lotus_dashboard.models import *

from utils.llcrmapi import LLCRMAPI
from utils.llcrmhook import LLCRMHook


def task_update_campaigns():
    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list[:2]:
        llcrm_api = LLCRMAPI(crm.crm_url, crm.api_username, crm.api_password)
        campaigns = llcrm_api.campaigns()
        if campaigns['response_code'] != "100":
            print(crm.crm_name, campaigns['response_code'])
            continue

        campaigns = campaigns['campaigns']
        for key, value in campaigns.items():
            campaign_id = int(value['campaign_id'])
            campaign_name = value['campaign_name'].strip()
            if LabelCampaign.objects.filter(crm=crm).filter(campaign_id=campaign_id).exists():
                label_campaign = LabelCampaign.objects.get(crm=crm, campaign_id=campaign_id)
                label_campaign.campaign_name = campaign_name
                print(crm.id, campaign_id, campaign_name, 'updated')
            else:
                label_campaign = LabelCampaign.objects.create(
                    crm=crm,
                    campaign_id=campaign_id,
                    campaign_name=campaign_name,
                )
                print(crm.id, campaign_id, campaign_name, 'created')
            label_campaign.save()


def task_get_dashboard_sales(from_date, to_date):
    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list:
        llcrmhook = LLCRMHook(crm.id)
        crm_results = llcrmhook.get_crm_sales(from_date, to_date)
        for result in crm_results:
            crm_result = CrmResult()
            crm_result.from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
            crm_result.to_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
            crm_result.crm = crm
            crm_result.label_id = result['label_id']
            crm_result.goal = result['label_goal']
            crm_result.step1 = result['step1']
            crm_result.step2 = result['step2']
            crm_result.step1_nonpp = result['step1_nonpp']
            crm_result.step2_nonpp = result['step2_nonpp']
            crm_result.prepaids = result['prepaids']
            crm_result.prepaids_step1 = result['prepaids_step1']
            crm_result.prepaids_step2 = result['prepaids_step2']
            crm_result.tablet_step1 = result['tablet_step1']
            crm_result.tablet_step2 = result['tablet_step2']
            crm_result.order_count = result['order_count']
            crm_result.order_page = result['order_page']
            crm_result.declined = result['declined']
            crm_result.gross_order = result['gross_order']
            crm_result.save()
