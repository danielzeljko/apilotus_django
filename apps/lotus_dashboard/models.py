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


class BlockedIP(models.Model):
    ip = models.CharField(max_length=15)
    description = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('Blocked IP')
        verbose_name_plural = _('Blocked IPs')
        ordering = ['pk']

    def __str__(self):
        return self.ip


class Label(models.Model):
    name = models.CharField(max_length=32)
    type = models.IntegerField()

    class Meta:
        verbose_name = _('Label')
        verbose_name_plural = _('Labels')
        ordering = ['pk']

    def __str__(self):
        return self.name


class CrmAccountManager(models.Manager):

    def active_crm_accounts(self, permissions=None):
        """
        Returns active crm accounts
        """
        if permissions:
            return self.filter(paused=False).filter(pk__in=permissions)
        return self.filter(paused=False)

    def crm_accounts(self, permissions=None):
        """
        Returns all crm accounts
        """
        if permissions:
            return self.filter(pk__in=permissions)
        return self.all()


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

    class Meta:
        verbose_name = _('CRM Account')
        verbose_name_plural = _('CRM Accounts')
        ordering = ['pk']

    def __str__(self):
        return self.crm_name


class CrmResultManager(models.Manager):

    def check_crm_result(self, crm, from_date, to_date):
        return self.filter(crm=crm).filter(from_date=from_date).filter(to_date=to_date).exists()

    def get_crm_result(self, crm, from_date, to_date):
        return self.filter(crm=crm).filter(from_date=from_date).filter(to_date=to_date).values()


class CrmResult(models.Model):
    from_date = models.DateField()
    to_date = models.DateField()

    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True, blank=True)

    goal = models.IntegerField()
    step1 = models.IntegerField()
    step2 = models.IntegerField()
    tablet_step1 = models.IntegerField()
    tablet_step2 = models.IntegerField()
    prepaid = models.IntegerField()
    step1_non_prepaid = models.IntegerField()
    step2_non_prepaid = models.IntegerField()
    order_page = models.FloatField()
    order_count = models.IntegerField()
    decline = models.IntegerField()
    gross_order = models.IntegerField()
    prepaid_step1 = models.IntegerField()
    prepaid_step2 = models.IntegerField()

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    objects = CrmResultManager

    class Meta:
        verbose_name = _('CRM Result')
        verbose_name_plural = _('CRM Results')
        ordering = ['pk']

    def __str__(self):
        return str(self.from_date) + '~' + str(self.to_date) + ', ' + self.crm.crm_name + (' - ' + self.label.name if self.label else '')


class LabelGoal(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True, blank=True)
    goal = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Label Goal')
        verbose_name_plural = _('Label Goals')
        ordering = ['pk']

    def __str__(self):
        return self.crm.crm_name + '-' + self.label.name + '-' + str(self.goal)


CAMPAIGN_TYPE = (
    (1, 'Step1'),
    (2, 'Step2'),
    (3, 'Prepaids'),
    (4, 'Tablet'),
)

CAMPAIGN_FORMAT = (
    (1, 'Step1'),
    (2, 'Step2'),
    (5, 'Desktop'),
    (6, 'Mobile'),
)


class LabelCampaign(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    campaign_id = models.IntegerField()
    campaign_name = models.CharField(max_length=128)
    campaign_type = models.IntegerField(choices=CAMPAIGN_TYPE, null=True, blank=True)
    campaign_format = models.IntegerField(choices=CAMPAIGN_FORMAT, null=True, blank=True)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _('Label Campaign')
        verbose_name_plural = _('Label Campaigns')
        ordering = ['pk']

    def __str__(self):
        return self.crm.crm_name + '-' + str(self.campaign_id)

    def campaign_label(self):
        campaign_type = dict(CAMPAIGN_TYPE)[self.campaign_type] if self.campaign_type else ''
        campaign_format = dict(CAMPAIGN_FORMAT)[self.campaign_format] if self.campaign_format else ''
        label = self.label.name if self.label else ''
        if campaign_type or campaign_format or label:
            return ' '.join([campaign_type, campaign_format, label])
        return ''
