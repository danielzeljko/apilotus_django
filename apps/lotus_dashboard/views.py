from io import BytesIO

import xlsxwriter
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from lotus_dashboard.models import *
from lotus_dashboard.tasks import task_get_dashboard_sales, task_update_campaigns, task_get_initial_reports, \
    task_get_rebill_reports, task_get_sales_report

from apilotus import settings


@login_required
def dashboard(request):
    user = request.user
    crm_positions = user.crm_positions

    context = {
        'tab_name': 'Dashboard',
        'crm_positions': crm_positions,
        'alert_count': 7,   # $alert_count = $dbApi->getRecentAlertCount($userId);
    }
    return render(request, 'dashboard/dashboard.html', context=context)


@login_required
def view_initial_report(request):
    crm_list = CrmAccount.objects.active_crm_accounts()

    context = {
        'tab_name': 'Initial',
        'crm_list': crm_list,
    }
    return render(request, 'reports/initial_report.html', context=context)


@login_required
def view_rebill_report(request):
    rebill_list = [a.crm.id for a in Rebill.objects.all()]
    crm_list = CrmAccount.objects.active_crm_accounts()
    crm_list = [a for a in crm_list if a.id in rebill_list]

    context = {
        'tab_name': 'Rebill',
        'crm_list': crm_list,
    }
    return render(request, 'reports/rebill_report.html', context=context)


@login_required
def view_cap_update(request):
    context = {
        'tab_name': 'CAP Update',
    }
    return render(request, 'cap/cap_update.html', context=context)


@login_required
def view_affiliates(request):
    crm_list = CrmAccount.objects.active_crm_accounts()
    vertical_labels = OfferLabel.objects.all()

    context = {
        'tab_name': 'Affiliate Settings',
        'crm_list': crm_list,
        'vertical_labels': vertical_labels,
    }
    return render(request, 'cap/affiliate_offer.html', context=context)


@login_required
def view_billing_dashboard(request):
    crm_list = CrmAccount.objects.active_crm_accounts()

    context = {
        'tab_name': 'Billing',
        'crm_list': crm_list,
    }
    return render(request, 'billing/billing.html', context=context)


# ajax functions
def ajax_dashboard_columns_get(request):
    site = get_current_site(request)
    columns = DashboardColumn.objects.get(site=site)
    return HttpResponse(columns.columns)


def ajax_crm_list(request):
    user = request.user
    if user.is_staff:
        crm_list = CrmAccount.objects.active_crm_accounts()
    else:
        crm_permissions = user.crm_permissions.all()
        crm_list = CrmAccount.objects.active_crm_accounts(permissions=crm_permissions)

    return JsonResponse(list(crm_list.values()), safe=False)


def ajax_setting_crm_list(request):
    user = request.user
    if user.is_staff:
        crm_list = CrmAccount.objects.crm_accounts()
    else:
        crm_permissions = user.crm_permissions.all()
        crm_list = CrmAccount.objects.crm_accounts(permissions=crm_permissions)

    return JsonResponse(list(crm_list.values()), safe=False)


def ajax_setting_crm_goal(request):
    crm_ids = request.GET['crm_ids'].split(',')
    crm_goals = request.GET['crm_goals'].split(',')
    for idx, crm_id in enumerate(crm_ids):
        crm = CrmAccount.objects.get(id=int(crm_id))
        if crm.sales_goal != int(crm_goals[idx]):
            crm.sales_goal = int(crm_goals[idx])
            crm.save()

    return HttpResponse('OK')


def ajax_setting_crm_add(request):
    crm = CrmAccount()
    crm.crm_name = request.GET['crm_name']
    crm.crm_url = request.GET['crm_url']
    crm.username = request.GET['crm_username']
    crm.password = request.GET['crm_password']
    crm.api_username = request.GET['api_username']
    crm.api_password = request.GET['api_password']
    crm.sales_goal = int(request.GET['sales_goal'])
    crm.rebill_length = int(request.GET['rebill_length'])
    crm.test_cc = request.GET['test_cc']
    crm.paused = bool(int(request.GET['crm_paused']))
    crm.save()

    return HttpResponse('OK')


def ajax_setting_crm_edit(request):
    crm_id = int(request.GET['crm_id'])

    crm = CrmAccount.objects.get(id=crm_id)
    crm.crm_name = request.GET['crm_name']
    crm.crm_url = request.GET['crm_url']
    crm.username = request.GET['crm_username']
    if 'crm_password' in request.GET:
        crm.password = request.GET['crm_password']
    crm.api_username = request.GET['api_username']
    if 'api_password' in request.GET:
        crm.api_password = request.GET['api_password']
    crm.sales_goal = int(request.GET['sales_goal'])
    crm.paused = bool(int(request.GET['crm_paused']))
    if 'rebill_length' in request.GET:
        crm.rebill_length = int(request.GET['rebill_length'])
    if 'test_cc' in request.GET:
        crm.test_cc = request.GET['test_cc']
    crm.save()

    return HttpResponse('OK')


def ajax_setting_crm_delete(request):
    return HttpResponse('OK')


def ajax_crm_position_set(request):
    crm_positions = request.GET['crm_positions']
    user = request.user
    user.crm_positions = crm_positions
    user.save()

    return HttpResponse('OK')


def ajax_dashboard_sales_all(request):
    user = request.user
    from_date = timezone.datetime.strptime(request.GET['from_date'], "%m/%d/%Y").date()
    to_date = timezone.datetime.strptime(request.GET['to_date'], "%m/%d/%Y").date()
    if user.is_staff:
        crm_list = CrmAccount.objects.active_crm_accounts()
    else:
        crm_permissions = user.crm_permissions.all()
        crm_list = CrmAccount.objects.active_crm_accounts(permissions=crm_permissions)

    crm_results = []
    for crm in crm_list:
        crm_results += CrmResult.objects.filter(crm=crm).filter(from_date=from_date).filter(to_date=to_date).values()
    for crm in crm_results:
        crm['label_name'] = Label.objects.get(id=crm['label_id']).name if crm['label_id'] else ''
    return JsonResponse(crm_results, safe=False)


def ajax_initial_list(request):
    crm_id = int(request.GET['crm_id'])
    from_date = timezone.datetime.strptime(request.GET['from_date'], "%m/%d/%Y").date()
    to_date = timezone.datetime.strptime(request.GET['to_date'], "%m/%d/%Y").date()

    try:
        initial_result = InitialResult.objects.get(from_date=from_date, to_date=to_date, crm_id=crm_id)
        return JsonResponse(initial_result.result, safe=False)
    except InitialResult.DoesNotExist:
        return JsonResponse('[]', safe=False)


def ajax_rebill_list(request):
    crm_id = int(request.GET['crm_id'])
    from_date = timezone.datetime.strptime(request.GET['from_date'], "%m/%d/%Y").date()
    to_date = timezone.datetime.strptime(request.GET['to_date'], "%m/%d/%Y").date()

    try:
        rebill_result = RebillResult.objects.get(from_date=from_date, to_date=to_date, crm_id=crm_id)
        return JsonResponse(rebill_result.result, safe=False)
    except RebillResult.DoesNotExist:
        return JsonResponse('[]', safe=False)


def export_billing_report(request):
    affiliate_id = int(request.GET['affiliate_id'])
    from_date = request.GET['from_date']
    to_date = request.GET['to_date']

    affiliate = Affiliate.objects.get(id=affiliate_id)

    output_file_name = 'billing_%s_%s-%s' % (affiliate.name, from_date.replace('/', '.'), to_date.replace('/', '.'))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + output_file_name + '.xlsx'

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(from_date.replace('/', '.') + '-' + to_date.replace('/', '.'))

    worksheet.set_column(0, 0, 18)
    worksheet.set_column(1, 1, 25)
    worksheet.set_column(2, 2, 5)
    worksheet.set_column(3, 3, 30)
    worksheet.set_column(6, 6, 14)

    cell_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#5B9BD5'})
    worksheet.write('A1', 'Affiliate', cell_format)
    worksheet.write('A2', 'Affiliate ID', cell_format)
    worksheet.write('A3', 'Week Of', cell_format)
    worksheet.write('A4', 'Total To Invoice', cell_format)

    cell_format = workbook.add_format({'align': 'left'})
    worksheet.write('B1', affiliate.name, cell_format)
    worksheet.write('B2', affiliate.afid, cell_format)
    worksheet.write('B3', from_date + '-' + to_date, cell_format)

    cell_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'bg_color': '#C6EFCE', 'align': 'center'})
    worksheet.write('D1', 'Offer', cell_format)
    worksheet.write('E1', 'Sales', cell_format)
    worksheet.write('F1', 'CPA', cell_format)
    worksheet.write('G1', 'Total', cell_format)

    from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
    to_date = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()

    affiliate_offers = AffiliateOffer.objects.filter(affiliate=affiliate)
    row = 2
    total_tti = 0
    for affiliate_offer in affiliate_offers:
        offer = affiliate_offer.offer
        cell_format = workbook.add_format({'bold': True, 'align': 'center'})
        worksheet.write('D' + str(row), offer.name, cell_format)

        cpa = affiliate_offer.s1_payout if affiliate_offer.s1_payout else offer.s1_payout
        worksheet.write('F' + str(row), "$ {:,.2f}".format(cpa))

        try:
            cap_update_result = CapUpdateResult.objects.get(crm=offer.crm, from_date=from_date, to_date=to_date)
            afids = affiliate.afid.split(',')
            campaign_ids = affiliate_offer.offer.step1.all()
            cap_result = eval(cap_update_result.result)
            specials = []

            sales = 0
            for prospect in cap_result:
                for campaign_id in campaign_ids:
                    if campaign_id.campaign_id == prospect[0]:
                        for prospect_data in prospect[1]:
                            for afid in afids:
                                if prospect_data['id'] == afid.split('(')[0]:
                                    if len(afid.split('(')) == 2:
                                        pass
                                    else:
                                        sales += prospect_data['initial_customers']

            cell_format = workbook.add_format({'align': 'center'})
            worksheet.write('E' + str(row), sales if sales else None, cell_format)

            tti = sales * cpa
            worksheet.write('G' + str(row), "$ {:,.2f}".format(tti) if tti else "$  -")

            total_tti += tti
        except CapUpdateResult.DoesNotExist:
            pass
        row += 1

    worksheet.write('B4', "$ {:,.2f}".format(total_tti))

    workbook.close()
    xlsx_data = output.getvalue()

    response.write(xlsx_data)
    return response

def view_update_campaigns(request):
    task_update_campaigns()
    return redirect('/' + settings.LOTUS_ADMIN_URL)


def view_get_dashboard_sales(request):
    task_get_dashboard_sales()
    return redirect('lotus_dashboard:dashboard')


def view_get_initial_reports(request):
    today = timezone.datetime.now().date()
    week_start = today + timezone.timedelta(-today.weekday())
    task_get_initial_reports(week_start.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y'))
    return redirect('/' + settings.LOTUS_ADMIN_URL)


def view_get_rebill_reports(request):
    cur_date = timezone.datetime.now().date()
    from_date = cur_date - timezone.timedelta(days=cur_date.weekday() + 22)
    to_date = from_date + timezone.timedelta(days=6)
    task_get_rebill_reports(from_date.strftime('%m/%d/%Y'), to_date.strftime('%m/%d/%Y'))
    return redirect('/' + settings.LOTUS_ADMIN_URL)


def view_get_cap_update_result(request):
    task_get_sales_report()
    return redirect('lotus_dashboard:cap_update')
