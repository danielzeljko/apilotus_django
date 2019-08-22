from django.contrib import admin

from lotus_alert.models import *


class AlertTypeAdmin(admin.ModelAdmin):
    list_filter = ['alert_name', 'status']
    list_display = ['alert_name', 'alert_formula', 'report_date', 'alert_day', 'alert_hour', 'sms', 'email', 'bot', 'status']


class AlertSettingAdmin(admin.ModelAdmin):
    list_filter = ['crm']

    list_display = ['crm', 'type', 'value1', 'value2']


class AlertStatusAdmin(admin.ModelAdmin):
    list_filter = ['crm', 'type']

    list_display = ['crm', 'type', 'value', 'level', 'status', 'alert_read', 'alert_delete', 'from_date', 'to_date', 'timestamp']


admin.site.register(AlertType, AlertTypeAdmin)
admin.site.register(AlertSetting, AlertSettingAdmin)
admin.site.register(AlertStatus, AlertStatusAdmin)
