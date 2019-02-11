from django.utils.translation import gettext_lazy as _

from django.contrib.sites.models import Site
from django.db import models


class DashboardColumn(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    columns = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('Dashboard Column')
        verbose_name_plural = _('Dashboard Columns')
        ordering = ['pk']


class CrmAccountManager(models.Manager):

    def active_crm_accounts(self, permissions=None):
        """
        Returns active crm accounts
        """
        if permissions:
            return self.filter(paused=False).filter(pk__in=permissions)
        return self.filter(paused=False)


class CrmAccount(models.Model):
    crm_name = models.CharField(max_length=100, unique=True)
    crm_url = models.URLField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    api_username = models.CharField(max_length=100)
    api_password = models.CharField(max_length=100)
    sales_goal = models.IntegerField(default=0)
    paused = models.BooleanField(default=False)
    password_updated = models.DateField(null=True, blank=True)
    rebill_length = models.IntegerField(null=True, blank=True)
    test_cc = models.CharField(max_length=16, null=True, blank=True)

    objects = CrmAccountManager()

    def __str__(self):
        return self.crm_name

    class Meta:
        verbose_name = _('CRM Account')
        verbose_name_plural = _('CRM Accounts')
        ordering = ['pk']
