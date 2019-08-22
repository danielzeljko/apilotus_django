from rest_framework import serializers
from lotus_alert.models import *


class AlertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertType
        fields = ('id', 'alert_name', 'alert_formula', 'report_date', 'alert_day', 'alert_hour', 'sms', 'email', 'bot', 'status')


class AlertStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertStatus
        fields = ('id', 'crm', 'type', 'value', 'level', 'status', 'alert_read', 'alert_delete', 'from_date', 'to_date', 'timestamp')
