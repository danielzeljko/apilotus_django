from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render
from lotus_dashboard.models import *

import datetime


@login_required
def dashboard(request):
    user = request.user
    crm_positions = user.crm_positions
    context = {
        'tab_name': 'Dashboard',
        'crm_positions': crm_positions
    }
    return render(request, 'dashboard/dashboard.html', context=context)


def view_dashboard_columns_get(request):
    site = get_current_site(request)
    columns = DashboardColumn.objects.get(site=site)
    return HttpResponse('["success", "{}"]'.format(columns.columns))


def view_crm_list(request):
    user = request.user
    if user.is_staff:
        crm_list = CrmAccount.objects.active_crm_accounts()
    else:
        crm_permissions = user.crm_permissions.all()
        crm_list = CrmAccount.objects.active_crm_accounts(permissions=crm_permissions)

    result = []
    for crm in crm_list:
        result.append(
            [crm.id, crm.crm_name, crm.crm_url, crm.username, crm.password, crm.api_username, crm.api_password,
             crm.sales_goal, 1 if crm.paused else 0, crm.password_updated.strftime("%Y-%m-%d"),
             datetime.datetime.now().strftime("%Y-%m-%d"),
             crm.rebill_length, crm.test_cc]
        )
    return HttpResponse(str(result).replace("'", '"'))
