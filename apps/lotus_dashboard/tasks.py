from django.utils import timezone

from lotus_dashboard.models import *

from utils.llcrmapi import LLCRMAPI
from utils.llcrmhook import LLCRMHook


def task_update_campaigns():
    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list[3:4]:
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
    for crm in crm_list[1:2]:
        llcrm_hook = LLCRMHook(crm.id)
        crm_results = llcrm_hook.get_crm_sales(from_date, to_date)
        from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
        to_date = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()
        for result in crm_results:
            try:
                crm_result = CrmResult.objects.get(from_date=from_date, to_date=to_date, crm=crm, label_id=result['label_id'])
            except CrmResult.DoesNotExist:
                crm_result = CrmResult()
                crm_result.from_date = from_date
                crm_result.to_date = to_date
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


def task_get_initial_reports(from_date, to_date, cycle=1):
    crm_list = CrmAccount.objects.active_crm_accounts()

    for crm in crm_list[1:2]:
        results = []
        llcrm_hook = LLCRMHook(crm.id)
        retentions = llcrm_hook.get_retention_report(from_date, to_date)
        campaigns = [a.campaign_id for a in LabelCampaign.objects.filter(campaign_type__isnull=False)]
        print([a['campaign_id'] for a in retentions])
        for retention in retentions:
            if retention['campaign_id'] in campaigns:
                aids = []
                print(retention['campaign_id'])
                if retention['has_affiliate']:
                    aid_results = llcrm_hook.get_retention_report_by_campaign(from_date, to_date, cycle, retention['campaign_id'])
                    for aid_result in aid_results:
                        print(aid_result)
                        sub_results = llcrm_hook.get_retention_report_by_affiliate(from_date, to_date, cycle, retention['campaign_id'], aid_result['affiliate_id'])
                        print(sub_results)
                        sub_results = [[a['sub_affiliate_name'], '', a['net_approved'], a['declined'],
                                        '%.2f' % (a['net_approved'] * 100 / a['gross_orders'])] for a in sub_results]
                        aids.append([[aid_result['affiliate_id'], aid_result['affiliate_name'], aid_result['net_approved'], aid_result['declined'],
                                      '%.2f' % (aid_result['net_approved'] * 100 / aid_result['gross_orders'])], sub_results])
                results.append([[
                    retention['campaign_id'], retention['campaign_name'], retention['net_approved'], retention['gross_orders'],
                    '%.2f' % (retention['net_approved'] * 100 / retention['gross_orders'])], aids])

        from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
        to_date = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()
        try:
            initial_result = InitialResult.objects.get(from_date=from_date, to_date=to_date, crm=crm)
        except InitialResult.DoesNotExist:
            initial_result = InitialResult()
            initial_result.from_date = from_date
            initial_result.to_date = to_date
            initial_result.crm = crm
        initial_result.result = str(results)
        initial_result.save()


def task_get_rebill_reports(from_date, to_date, cycle=2):
    crm_list = Rebill.objects.all()

    for crm in crm_list:
        results = []
        llcrm_hook = LLCRMHook(crm.crm_id)
        retentions = llcrm_hook.get_retention_report(from_date, to_date, cycle)
        rebills = [a.campaign_id for a in crm.rebills.all()]
        for retention in retentions:
            if retention['campaign_id'] in rebills:
                if retention['gross_orders'] <= 10:
                    continue
                aids = []
                print(retention['campaign_id'])
                if retention['has_affiliate']:
                    aid_results = llcrm_hook.get_retention_report_by_campaign(from_date, to_date, cycle, retention['campaign_id'])
                    for aid_result in aid_results:
                        if aid_result['gross_orders'] <= 10:
                            continue
                        print(aid_result)
                        sub_results = llcrm_hook.get_retention_report_by_affiliate(from_date, to_date, cycle, retention['campaign_id'], aid_result['affiliate_id'])
                        print(sub_results)
                        sub_results = [[a['sub_affiliate_name'], '', a['net_approved'], a['declined'],
                                        '%.2f' % (a['net_approved'] * 100 / a['gross_orders'])] for a in sub_results if a['gross_orders'] > 10]
                        aids.append([[aid_result['affiliate_id'], aid_result['affiliate_name'], aid_result['net_approved'], aid_result['declined'],
                                      '%.2f' % (aid_result['net_approved'] * 100 / aid_result['gross_orders'])], sub_results])
                results.append([[
                    retention['campaign_id'], retention['campaign_name'], retention['net_approved'], retention['gross_orders'],
                    '%.2f' % (retention['net_approved'] * 100 / retention['gross_orders'])], aids])

        from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
        to_date = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()
        try:
            rebill_result = RebillResult.objects.get(from_date=from_date, to_date=to_date, crm=crm)
        except RebillResult.DoesNotExist:
            rebill_result = RebillResult()
            rebill_result.from_date = from_date
            rebill_result.to_date = to_date
            rebill_result.crm = crm
        rebill_result.result = str(results)
        rebill_result.save()


def task_get_sales_report(from_date, to_date, campaign_id='', aff='', f='', sf=''):
    crm_list = CrmAccount.objects.active_crm_accounts()

    for crm in crm_list:
        if crm.id != 2:
            continue
        results = []
        llcrm_hook = LLCRMHook(crm.id)
        campaign_results = llcrm_hook.get_sales_report_for_cap_update(from_date, to_date, '', '', '', '')
        for campaign_result in campaign_results[:-1]:
            sub_result = llcrm_hook.get_sales_report_for_cap_update(from_date, to_date, '', '1', campaign_result['id'], '0')
            results.append([int(campaign_result['id']), sub_result[:-1]])

        from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
        to_date = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()
        try:
            cap_update_result = CapUpdateResult.objects.get(from_date=from_date, to_date=to_date, crm=crm)
        except CapUpdateResult.DoesNotExist:
            cap_update_result = CapUpdateResult()
            cap_update_result.from_date = from_date
            cap_update_result.to_date = to_date
            cap_update_result.crm = crm
        cap_update_result.result = str(results)
        cap_update_result.save()
