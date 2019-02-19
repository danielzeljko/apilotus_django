from django.contrib import admin

from lotus_alert.models import *


class AlertTypeAdmin(admin.ModelAdmin):
    list_filter = ['alert_name', 'status']
    list_display = ['alert_name', 'alert_formula', 'report_date', 'alert_day', 'alert_hour', 'sms', 'email', 'bot', 'status']


class AlertSettingAdmin(admin.ModelAdmin):
    list_display = ['crm', 'type', 'value1', 'value2']


admin.site.register(AlertType, AlertTypeAdmin)
admin.site.register(AlertSetting, AlertSettingAdmin)
