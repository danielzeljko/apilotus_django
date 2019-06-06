from django.utils import timezone

from celery.schedules import crontab
from celery.task import task, periodic_task

from lotus_dashboard.models import *

from utils.llcrmapi import LLCRMAPI
from utils.llcrmhook import LLCRMHook


@periodic_task(
    run_every=(crontab(minute=1, hour=0)),
    name="apps.lotus_dashboard.tasks.task_update_campaigns",
    ignore_result=True,
)
def task_update_campaigns():
    crm_list = CrmAccount.objects.all()
    for crm in crm_list:
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


def save_crm_results(crm_results, from_date, to_date, crm_id):
    for result in crm_results:
        try:
            crm_result = CrmResult.objects.get(from_date=from_date, to_date=to_date, crm_id=crm_id,
                                               label_id=result['label_id'])
        except CrmResult.DoesNotExist:
            crm_result = CrmResult()
            crm_result.from_date = from_date
            crm_result.to_date = to_date
            crm_result.crm_id = crm_id
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


@periodic_task(
    run_every=(crontab(minute='*/29')),
    name="apps.lotus_dashboard.tasks.task_get_dashboard_sales",
    ignore_result=True,
)
def task_get_dashboard_sales():
    today = timezone.datetime.now().date()
    yesterday = today + timezone.timedelta(-1)
    week_start = today + timezone.timedelta(-today.weekday())

    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list:
        print(crm)
        llcrm_hook = LLCRMHook(crm.id)

        # Week To Date
        crm_results = llcrm_hook.get_crm_sales(week_start.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'))
        save_crm_results(crm_results, week_start, today, crm.id)

        # Today
        crm_results = llcrm_hook.get_crm_sales(today.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'))
        save_crm_results(crm_results, today, today, crm.id)

        # Yesterday
        if not CrmResult.objects.filter(from_date=yesterday, to_date=yesterday, crm=crm).exists():
            crm_results = llcrm_hook.get_crm_sales(yesterday.strftime('%m/%d/%Y'), yesterday.strftime('%m/%d/%Y'))
            save_crm_results(crm_results, yesterday, yesterday, crm.id)


def task_get_initial_reports(from_date, to_date, cycle=1):
    crm_list = CrmAccount.objects.active_crm_accounts()
    from_date_ = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
    to_date_ = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()

    for crm in crm_list:
        print(crm)
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

        try:
            initial_result = InitialResult.objects.get(from_date=from_date_, to_date=to_date_, crm=crm)
        except InitialResult.DoesNotExist:
            initial_result = InitialResult()
            initial_result.from_date = from_date_
            initial_result.to_date = to_date_
            initial_result.crm = crm
        initial_result.result = str(results)
        initial_result.save()


def task_get_rebill_reports(from_date, to_date, cycle=2):
    rebill_list = Rebill.objects.filter(crm__paused=False)
    from_date_ = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
    to_date_ = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()

    for rebill in rebill_list:
        print(rebill.crm)
        results = []
        llcrm_hook = LLCRMHook(rebill.crm_id)
        retentions = llcrm_hook.get_retention_report(from_date, to_date, cycle)
        rebills = [a.campaign_id for a in rebill.rebills.all()]
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

        try:
            rebill_result = RebillResult.objects.get(from_date=from_date_, to_date=to_date_, crm=rebill.crm)
        except RebillResult.DoesNotExist:
            rebill_result = RebillResult()
            rebill_result.from_date = from_date_
            rebill_result.to_date = to_date_
            rebill_result.crm = rebill.crm
        rebill_result.result = str(results)
        rebill_result.save()


def save_cap_update_results(results, from_date, to_date, crm_id):
    try:
        cap_update_result = CapUpdateResult.objects.get(from_date=from_date, to_date=to_date, crm=crm_id)
    except CapUpdateResult.DoesNotExist:
        cap_update_result = CapUpdateResult()
        cap_update_result.from_date = from_date
        cap_update_result.to_date = to_date
        cap_update_result.crm_id = crm_id
    cap_update_result.result = str(results)
    cap_update_result.save()


@periodic_task(
    run_every=(crontab(minute='*/59')),
    name="apps.lotus_dashboard.tasks.task_get_sales_report",
    ignore_result=True,
)
def task_get_sales_report():
    today = timezone.datetime.now().date()
    yesterday = today + timezone.timedelta(-1)
    week_start = today + timezone.timedelta(-today.weekday())

    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list:
        print(crm)
        llcrm_hook = LLCRMHook(crm.id)

        # Week To Date
        results = []
        campaign_results = llcrm_hook.get_sales_report_for_cap_update(week_start.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'), '', '', '', '')
        for campaign_result in campaign_results[:-1]:
            sub_result = llcrm_hook.get_sales_report_for_cap_update(week_start.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'), '', '1', campaign_result['id'], '0')
            results.append([int(campaign_result['id']), sub_result[:-1]])
        save_cap_update_results(results, week_start, today, crm.id)

        # Today
        results = []
        campaign_results = llcrm_hook.get_sales_report_for_cap_update(today.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'), '', '', '', '')
        for campaign_result in campaign_results[:-1]:
            sub_result = llcrm_hook.get_sales_report_for_cap_update(today.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'), '', '1', campaign_result['id'], '0')
            results.append([int(campaign_result['id']), sub_result[:-1]])
        save_cap_update_results(results, today, today, crm.id)

        # Yesterday
        if not CapUpdateResult.objects.filter(from_date=yesterday, to_date=yesterday, crm=crm).exists():
            results = []
            campaign_results = llcrm_hook.get_sales_report_for_cap_update(yesterday.strftime('%m/%d/%Y'), yesterday.strftime('%m/%d/%Y'), '', '', '', '')
            for campaign_result in campaign_results[:-1]:
                sub_result = llcrm_hook.get_sales_report_for_cap_update(yesterday.strftime('%m/%d/%Y'), yesterday.strftime('%m/%d/%Y'), '', '1', campaign_result['id'], '0')
                results.append([int(campaign_result['id']), sub_result[:-1]])
            save_cap_update_results(results, yesterday, yesterday, crm.id)


def save_billing_results(billing, trial_result, mc_result, from_date, to_date):
    try:
        billing_result = BillingResult.objects.get(from_date=from_date, to_date=to_date, billing=billing)
    except BillingResult.DoesNotExist:
        billing_result = BillingResult()
        billing_result.from_date = from_date
        billing_result.to_date = to_date
        billing_result.billing = billing
    billing_result.trial_result = str(trial_result)
    billing_result.mc_result = str(mc_result)
    billing_result.save()


@periodic_task(
    run_every=(crontab(minute='*/39')),
    name="apps.lotus_dashboard.tasks.task_get_billing_report",
    ignore_result=True,
)
def task_get_billing_report():
    today = timezone.datetime.now().date()
    week_start = today + timezone.timedelta(-today.weekday())
    week_end = week_start + timezone.timedelta(6)
    billings = OfferBilling.objects.all()

    for billing in billings:
        print(billing)
        crm = billing.offer.crm
        llcrm_hook = LLCRMHook(crm.id)
        trial_desktop = llcrm_hook.get_sales_report_for_billing(week_start.strftime('%m/%d/%Y'), week_end.strftime('%m/%d/%Y'), billing.trial_desktop.campaign_id)
        trial_mobile = llcrm_hook.get_sales_report_for_billing(week_start.strftime('%m/%d/%Y'), week_end.strftime('%m/%d/%Y'), billing.trial_mobile.campaign_id)
        mc_desktop = llcrm_hook.get_sales_report_for_billing(week_start.strftime('%m/%d/%Y'), week_end.strftime('%m/%d/%Y'), billing.mc_desktop.campaign_id)
        mc_mobile = llcrm_hook.get_sales_report_for_billing(week_start.strftime('%m/%d/%Y'), week_end.strftime('%m/%d/%Y'), billing.mc_mobile.campaign_id)

        trial_result = trial_desktop + trial_mobile
        mc_result = mc_desktop + mc_mobile
        save_billing_results(billing, trial_result, mc_result, week_start, week_end)
