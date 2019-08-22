from io import BytesIO

import xlsxwriter
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from lotus_alert.models import AlertStatus
from lotus_dashboard.models import *
from lotus_dashboard.tasks import task_get_dashboard_sales, task_update_campaigns, task_get_initial_reports, \
    task_get_rebill_reports, task_get_sales_report, task_get_billing_report

from apilotus import settings


@login_required
def dashboard(request):
    user = request.user
    site = get_current_site(request)
    crm_positions = user.crm_positions
    alert_counts = AlertStatus.objects.filter(status=False).count()
    columns = DashboardColumn.objects.get(user=user, site=site)

    context = {
        'tab_name': 'Dashboard',
        'crm_positions': crm_positions,
        'alert_count': alert_counts,
        'columns': columns.columns,
        'columns_list': columns.columns.split(','),
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


@login_required
def view_billing_report(request):
    crm_list = CrmAccount.objects.active_crm_accounts()

    context = {
        'tab_name': 'Billing Reports',
        'crm_list': crm_list,
    }
    return render(request, 'billing/billing_report.html', context=context)


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


def ajax_setting_crm_column(request):
    crm_column = request.GET['crm_column']

    user = request.user
    site = get_current_site(request)
    columns = DashboardColumn.objects.get(user=user, site=site)
    columns.columns = crm_column
    columns.save()

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

    affiliate = BillingAffiliate.objects.get(id=affiliate_id)

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

    billing_results = BillingResult.objects.filter(from_date=from_date, to_date=to_date)

    total = 0
    row = 2

    afids = affiliate.afid.split(', ')
    for result in billing_results:
        trial_results = eval(result.trial_result)
        mc_results = eval(result.mc_result)
        trial_count = 0
        mc_count = 0
        trial_cpa = 0
        mc_cpa = 0
        for afid in afids:
            afid_id = afid.split('(')[0]
            cpa = afid.split('(')[1][:-1]

            for trial_result in trial_results:
                if afid_id == trial_result['id']:
                    trial_cpa = int(cpa.split(',')[0])
                    trial_count += int(trial_result['initial_customers'])
                    total += trial_cpa * int(trial_result['initial_customers'])

            for mc_result in mc_results:
                if afid_id == mc_result['id']:
                    mc_cpa = int(cpa.split(',')[1] if len(cpa.split(',')) > 1 else cpa)
                    mc_count += int(mc_result['initial_customers'])
                    total += mc_cpa * int(mc_result['initial_customers'])

        offer = result.billing.offer
        if affiliate.name == 'MaxBounty':
            if trial_count > 0 or mc_count > 0:
                cell_format = workbook.add_format({'bold': True, 'align': 'center'})
                worksheet.write('D' + str(row), offer.name, cell_format)
                worksheet.write('F' + str(row), "$ {:,.2f}".format(trial_cpa))
                cell_format = workbook.add_format({'align': 'center'})
                worksheet.write('E' + str(row), str(trial_count + mc_count), cell_format)
                tti = (trial_count + mc_count) * trial_cpa
                worksheet.write('G' + str(row), "$ {:,.2f}".format(tti) if tti else "$  -")
                row += 1
        else:
            if trial_count > 0:
                cell_format = workbook.add_format({'bold': True, 'align': 'center'})
                worksheet.write('D' + str(row), offer.name + ' Trial', cell_format)
                worksheet.write('F' + str(row), "$ {:,.2f}".format(trial_cpa))
                cell_format = workbook.add_format({'align': 'center'})
                worksheet.write('E' + str(row), str(trial_count), cell_format)
                tti = trial_count * trial_cpa
                worksheet.write('G' + str(row), "$ {:,.2f}".format(tti) if tti else "$  -")
                row += 1
            if mc_count > 0:
                cell_format = workbook.add_format({'bold': True, 'align': 'center'})
                worksheet.write('D' + str(row), offer.name + ' MC', cell_format)
                worksheet.write('F' + str(row), "$ {:,.2f}".format(mc_cpa))
                cell_format = workbook.add_format({'align': 'center'})
                worksheet.write('E' + str(row), str(mc_count), cell_format)
                tti = mc_count * mc_cpa
                worksheet.write('G' + str(row), "$ {:,.2f}".format(tti) if tti else "$  -")
                row += 1

    worksheet.write('B4', "$ {:,.2f}".format(total))

    workbook.close()
    xlsx_data = output.getvalue()

    response.write(xlsx_data)
    return response


def export_billing_reports(request):
    from_date = request.GET['from_date']
    to_date = request.GET['to_date']

    output_file_name = 'billing_Total_%s-%s' % (from_date.replace('/', '.'), to_date.replace('/', '.'))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + output_file_name + '.xlsx'

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(from_date.replace('/', '.') + '-' + to_date.replace('/', '.'))

    worksheet.set_column(0, 0, 25)
    worksheet.set_column(1, 1, 25)
    worksheet.set_column(2, 2, 10)
    worksheet.set_column(3, 3, 30)
    worksheet.set_column(6, 6, 14)

    cell_format = workbook.add_format({'bold': True, 'font_color': '#5B9BD5', 'align': 'center'})
    worksheet.write('A1', 'Week of', cell_format)
    cell_format = workbook.add_format({'align': 'center'})
    worksheet.write('A2', from_date + ' - ' + to_date, cell_format)
    cell_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'bg_color': '#C6EFCE', 'align': 'right'})
    worksheet.write('A3', 'Affiliate', cell_format)
    worksheet.write('B3', 'AFF ID', cell_format)
    cell_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'bg_color': '#C6EFCE', 'align': 'center'})
    worksheet.write('C3', 'INV #', cell_format)
    worksheet.write('D3', 'Total Payment', cell_format)

    affiliates = BillingAffiliate.objects.all()
    billing_results = BillingResult.objects.filter(
        from_date=timezone.datetime.strptime(from_date, "%m/%d/%Y").date(),
        to_date=timezone.datetime.strptime(to_date, "%m/%d/%Y").date()
    )

    row = 4
    total_of_totals = 0
    for affiliate in affiliates:
        total = 0
        afids = affiliate.afid.split(', ')
        for result in billing_results:
            trial_results = eval(result.trial_result)
            mc_results = eval(result.mc_result)
            trial_count = 0
            mc_count = 0
            for afid in afids:
                afid_id = afid.split('(')[0]
                cpa = afid.split('(')[1][:-1]

                for trial_result in trial_results:
                    if afid_id == trial_result['id']:
                        trial_cpa = int(cpa.split(',')[0])
                        trial_count += int(trial_result['initial_customers'])
                        total += trial_cpa * int(trial_result['initial_customers'])

                for mc_result in mc_results:
                    if afid_id == mc_result['id']:
                        mc_cpa = int(cpa.split(',')[1] if len(cpa.split(',')) > 1 else cpa)
                        mc_count += int(mc_result['initial_customers'])
                        total += mc_cpa * int(mc_result['initial_customers'])

        total_of_totals += total
        cell_format = workbook.add_format({'bold': True, 'align': 'right'})
        worksheet.write('A' + str(row), affiliate.name, cell_format)
        cell_format = workbook.add_format({'align': 'right'})
        worksheet.write('B' + str(row), affiliate.afid, cell_format)
        worksheet.write('D' + str(row), "$ {:,.2f}".format(total) if total else "$  -")

        row += 1

    cell_format = workbook.add_format({'bold': True, 'align': 'right'})
    worksheet.write('C' + str(row), 'TOTAL', cell_format)
    cell_format = workbook.add_format({'bold': True})
    worksheet.write('D' + str(row), "$ {:,.2f}".format(total_of_totals) if total_of_totals else "$  -", cell_format)

    row += 3
    for affiliate in affiliates:
        cell_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#5B9BD5'})
        worksheet.write('A' + str(row), 'Affiliate', cell_format)
        worksheet.write('A' + str(row + 1), 'Affiliate ID', cell_format)
        worksheet.write('A' + str(row + 2), 'Week Of', cell_format)
        worksheet.write('A' + str(row + 3), 'Total To Invoice', cell_format)

        cell_format = workbook.add_format({'align': 'left'})
        worksheet.write('B' + str(row), affiliate.name, cell_format)
        worksheet.write('B' + str(row + 1), affiliate.afid, cell_format)
        worksheet.write('B' + str(row + 2), from_date + '-' + to_date, cell_format)

        cell_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'bg_color': '#C6EFCE', 'align': 'center'})
        worksheet.write('D' + str(row), 'Offer', cell_format)
        worksheet.write('E' + str(row), 'Sales', cell_format)
        worksheet.write('F' + str(row), 'CPA', cell_format)
        worksheet.write('G' + str(row), 'Total', cell_format)

        offer_row = row + 1
        total = 0
        afids = affiliate.afid.split(', ')
        for result in billing_results:
            trial_results = eval(result.trial_result)
            mc_results = eval(result.mc_result)
            trial_count = 0
            mc_count = 0
            trial_cpa = 0
            mc_cpa = 0
            for afid in afids:
                afid_id = afid.split('(')[0]
                cpa = afid.split('(')[1][:-1]

                for trial_result in trial_results:
                    if afid_id == trial_result['id']:
                        trial_cpa = int(cpa.split(',')[0])
                        trial_count += int(trial_result['initial_customers'])
                        total += trial_cpa * int(trial_result['initial_customers'])

                for mc_result in mc_results:
                    if afid_id == mc_result['id']:
                        mc_cpa = int(cpa.split(',')[1] if len(cpa.split(',')) > 1 else cpa)
                        mc_count += int(mc_result['initial_customers'])
                        total += mc_cpa * int(mc_result['initial_customers'])
            offer = result.billing.offer
            if affiliate.name == 'MaxBounty':
                if trial_count > 0 or mc_count > 0:
                    cell_format = workbook.add_format({'bold': True, 'align': 'center'})
                    worksheet.write('D' + str(offer_row), offer.name, cell_format)
                    worksheet.write('F' + str(offer_row), "$ {:,.2f}".format(trial_cpa))
                    cell_format = workbook.add_format({'align': 'center'})
                    worksheet.write('E' + str(offer_row), str(trial_count + mc_count), cell_format)
                    tti = (trial_count + mc_count) * trial_cpa
                    worksheet.write('G' + str(offer_row), "$ {:,.2f}".format(tti) if tti else "$  -")
                    offer_row += 1
            else:
                if trial_count > 0:
                    cell_format = workbook.add_format({'bold': True, 'align': 'center'})
                    worksheet.write('D' + str(offer_row), offer.name + ' Trial', cell_format)
                    worksheet.write('F' + str(offer_row), "$ {:,.2f}".format(trial_cpa))
                    cell_format = workbook.add_format({'align': 'center'})
                    worksheet.write('E' + str(offer_row), str(trial_count), cell_format)
                    tti = trial_count * trial_cpa
                    worksheet.write('G' + str(offer_row), "$ {:,.2f}".format(tti) if tti else "$  -")
                    offer_row += 1
                if mc_count > 0:
                    cell_format = workbook.add_format({'bold': True, 'align': 'center'})
                    worksheet.write('D' + str(offer_row), offer.name + ' MC', cell_format)
                    worksheet.write('F' + str(offer_row), "$ {:,.2f}".format(mc_cpa))
                    cell_format = workbook.add_format({'align': 'center'})
                    worksheet.write('E' + str(offer_row), str(mc_count), cell_format)
                    tti = mc_count * mc_cpa
                    worksheet.write('G' + str(offer_row), "$ {:,.2f}".format(tti) if tti else "$  -")
                    offer_row += 1

        worksheet.write('B' + str(row + 3), "$ {:,.2f}".format(total))
        row = offer_row + 2 if offer_row > row + 3 else row + 6

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
    task_get_initial_reports()
    return redirect('/' + settings.LOTUS_ADMIN_URL)


def view_get_rebill_reports(request):
    task_get_rebill_reports()
    return redirect('/' + settings.LOTUS_ADMIN_URL)


def view_get_cap_update_result(request):
    task_get_sales_report()
    return redirect('lotus_dashboard:cap_update')


def view_billing_result(request):
    task_get_billing_report()
    return redirect('lotus_dashboard:billing_dashboard')
