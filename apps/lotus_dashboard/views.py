from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from lotus_dashboard.models import *

import datetime
import requests
import json


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


def view_dashboard_columns_get(request):
    site = get_current_site(request)
    columns = DashboardColumn.objects.get(site=site)
    return HttpResponse(columns.columns)


def view_crm_list(request):
    user = request.user
    if user.is_staff:
        crm_list = CrmAccount.objects.active_crm_accounts()
    else:
        crm_permissions = user.crm_permissions.all()
        crm_list = CrmAccount.objects.active_crm_accounts(permissions=crm_permissions)

    return JsonResponse(list(crm_list.values()), safe=False)


def view_setting_crm_goal(request):
    crm_ids = request.GET['crm_ids'].split(',')
    crm_goals = request.GET['crm_goals'].split(',')
    for idx, crm_id in enumerate(crm_ids):
        crm = CrmAccount.objects.get(id=int(crm_id))
        if crm.sales_goal != int(crm_goals[idx]):
            crm.sales_goal = int(crm_goals[idx])
            crm.save()

    return HttpResponse('OK')


def view_setting_crm_edit(request):
    crm_id = int(request.GET['crm_id'])
    crm_name = request.GET['crm_name']
    crm_url = request.GET['crm_url']
    crm_username = request.GET['crm_username']
    api_username = request.GET['api_username']
    sales_goal = int(request.GET['sales_goal'])
    crm_paused = bool(int(request.GET['crm_paused']))

    crm = CrmAccount.objects.get(id=crm_id)
    crm.crm_name = crm_name
    crm.crm_url = crm_url
    crm.username = crm_username
    crm.api_username = api_username
    crm.sales_goal = sales_goal
    crm.paused = crm_paused
    crm.save()

    return HttpResponse('OK')


def view_crm_position_set(request):
    crm_positions = request.GET['crm_positions']
    user = request.user
    user.crm_positions = crm_positions
    user.save()

    return HttpResponse('OK')


def view_dashboard_sales_all(request):
    user = request.user
    # from_date = datetime.datetime.strptime(request.GET['from_date'], "%m/%d/%Y").date()
    # to_date = datetime.datetime.strptime(request.GET['to_date'], "%m/%d/%Y").date()
    from_date = datetime.datetime.strptime('02/11/2019', "%m/%d/%Y").date()
    to_date = datetime.datetime.strptime('02/15/2019', "%m/%d/%Y").date()
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


def view_get_dashboard_sales(request):
    id_convert_table = {
        1: 59, 2: 75, 3: 83, 4: 84, 5: 87, 6: 89, 7: 90, 8: 91, 9: 93,
        10: 94, 11: 95, 12: 96, 13: 97, 14: 98, 15: 100, 16: 101, 17: 102,
    }
    label_convert = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 12: 10, 14: 11, 31: 12}
    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list[1:]:
        url = 'https://dash.apilotus.com/daemon/ajax_admin/apis_for_django/dashboard_sales_wtd.php?crm_id={crm_id}'.format
        result = requests.get(url(crm_id=id_convert_table[crm.id]))
        result = json.loads(result.text)

        for sub_result in result[2]:
            if crm.id == 1 and sub_result[0] == 0:
                continue
            crm_result = CrmResult()
            crm_result.from_date = datetime.datetime.strptime(result[0], "%m/%d/%Y").date()
            crm_result.to_date = datetime.datetime.strptime(result[1], "%m/%d/%Y").date()
            crm_result.crm = crm
            crm_result.label_id = None if sub_result[0] == 0 else label_convert[int(sub_result[0])]
            crm_result.goal = crm.sales_goal if sub_result[0] == 0 else int(sub_result[2])
            crm_result.step1 = sub_result[3]
            crm_result.step2 = sub_result[4]
            crm_result.tablet_step1 = sub_result[5]
            crm_result.prepaid = sub_result[6]
            crm_result.step1_non_prepaid = sub_result[7]
            crm_result.step2_non_prepaid = sub_result[8]
            crm_result.order_page = sub_result[9]
            crm_result.order_count = sub_result[10]
            crm_result.decline = sub_result[11]
            crm_result.gross_order = sub_result[12]
            crm_result.prepaid_step1 = sub_result[13]
            crm_result.prepaid_step2 = sub_result[14]
            crm_result.tablet_step2 = sub_result[15]
            crm_result.save()
        print(result)

    return HttpResponse('OK')
