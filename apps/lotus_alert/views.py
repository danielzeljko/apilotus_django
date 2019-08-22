from django.http import JsonResponse, HttpResponse

from lotus_alert.models import *


def view_setting_alert_list_by_cid(request):
    crm_id = request.GET['crm_id']
    alert_settings = AlertSetting.objects.filter(crm_id=crm_id).values('id', 'crm_id', 'type_id', 'type__alert_name', 'value1', 'value2', 'type__alert_formula', 'type__report_date', 'type__status')

    result = []
    if not alert_settings:
        alert_types = AlertType.objects.all()
        for alert_type in alert_types:
            result.append({
                'id': 0,
                'crm_id': crm_id,
                'type_id': alert_type.id,
                'type__alert_name': alert_type.alert_name,
                'value1': 0,
                'value2': 0,
                'type__alert_formula': alert_type.alert_formula,
                'type__report_date': alert_type.report_date,
                'type__status': alert_type.status,
            })
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse(list(alert_settings), safe=False)


def view_setting_alert_edit(request):
    type_id = int(request.GET['type_id'])
    crm_id = int(request.GET['crm_id'])
    value1 = int(request.GET['value1'])
    value2 = int(request.GET['value2'])

    try:
        alert_setting = AlertSetting.objects.get(crm_id=crm_id, type_id=type_id)
        alert_setting.value1 = value1
        alert_setting.value2 = value2
    except AlertSetting.DoesNotExist:
        alert_setting = AlertSetting()
        alert_setting.crm_id = crm_id
        alert_setting.type_id = type_id
        alert_setting.value1 = value1
        alert_setting.value2 = value2
    alert_setting.save()
    return HttpResponse('OK')


def view_alert_recent_list(request):
    alert_status = AlertStatus.objects.filter(status=False).values('id', 'crm__crm_name', 'type', 'value', 'level',
                                                                   'from_date', 'to_date')
    return JsonResponse(list(alert_status), safe=False)


def view_alert_delete(request):
    alert_id = int(request.GET.get('alert_id', 0))
    alert = AlertStatus.objects.get(id=alert_id)
    alert.status = True
    alert.save()
    return HttpResponse('OK')


def view_alert_delete_all(request):
    alerts = AlertStatus.objects.all()
    for alert in alerts:
        alert.status = True
        alert.save()
    return HttpResponse('OK')
