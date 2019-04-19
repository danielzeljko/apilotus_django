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
    rebill_list = [a.crm.id for a in Rebill.objects.all()]
    crm_list = CrmAccount.objects.active_crm_accounts()
    crm_list = [a for a in crm_list if a.id in rebill_list]

    context = {
        'tab_name': 'CAP Update',
        'crm_list': crm_list,
    }
    return render(request, 'cap/cap_update.html', context=context)


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
