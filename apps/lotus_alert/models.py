from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from lotus_dashboard.models import CrmAccount


class AlertType(models.Model):
    alert_name = models.CharField(max_length=100)
    alert_formula = models.CharField(max_length=100)
    report_date = models.CharField(max_length=100, null=True, blank=True)
    alert_day = models.CharField(max_length=100, null=True, blank=True)
    alert_hour = models.CharField(max_length=100, null=True, blank=True)
    sms = models.BooleanField()
    email = models.BooleanField()
    bot = models.BooleanField()
    status = models.BooleanField()

    class Meta:
        verbose_name = _('Alert Type')
        verbose_name_plural = _('Alert Types')
        ordering = ['pk']

    def __str__(self):
        return self.alert_name


class AlertSetting(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    type = models.ForeignKey(AlertType, on_delete=models.CASCADE)
    value1 = models.IntegerField(default=0)
    value2 = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Alert Setting')
        verbose_name_plural = _('Alert Settings')
        ordering = ['pk']

    def __str__(self):
        return self.crm.crm_name + '-' + str(self.value1) + '/' + str(self.value2)
