from django.utils.translation import gettext_lazy as _

from django.contrib.sites.models import Site
from django.db import models

from apilotus import settings

try:
    User = settings.AUTH_USER_MODEL
except ImportError:
    from django.contrib.auth.models import User


class DashboardColumn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
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


class CrmToken(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    timestamp = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('CRM Token')
        verbose_name_plural = _('CRM Tokens')
        ordering = ['pk']

    def __str__(self):
        return self.crm.crm_name + ' - ' + self.token


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
    mc_step1 = models.IntegerField()
    mc_step2 = models.IntegerField()
    step1_nonpp = models.IntegerField()
    step2_nonpp = models.IntegerField()
    prepaids = models.IntegerField()
    prepaids_step1 = models.IntegerField()
    prepaids_step2 = models.IntegerField()
    tablet_step1 = models.IntegerField()
    tablet_step2 = models.IntegerField()
    order_count = models.IntegerField()
    order_page = models.FloatField()
    declined = models.IntegerField()
    gross_order = models.IntegerField()

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
    (5, 'MC Step1'),
    (6, 'MC Step2'),
)

CAMPAIGN_FORMAT = (
    (1, 'Step1'),
    (2, 'Step2'),
    (3, 'Desktop'),
    (4, 'Mobile'),
)


class LabelCampaign(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    campaign_id = models.IntegerField()
    campaign_name = models.CharField(max_length=128)
    campaign_type = models.IntegerField(choices=CAMPAIGN_TYPE, null=True, blank=True)
    campaign_format = models.IntegerField(choices=CAMPAIGN_FORMAT, null=True, blank=True)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True, blank=True)
    pid = models.CharField(verbose_name='Product IDs', max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Label Campaign')
        verbose_name_plural = _('Label Campaigns')
        ordering = ['pk']

    def __str__(self):
        return self.crm.crm_name + ' - ' + str(self.campaign_id) + (', ' if self.campaign_label else '') + self.campaign_label

    @property
    def campaign_label(self):
        campaign_type = dict(CAMPAIGN_TYPE)[self.campaign_type] if self.campaign_type else ''
        campaign_format = dict(CAMPAIGN_FORMAT)[self.campaign_format] if self.campaign_format else ''
        label = self.label.name if self.label else ''
        if campaign_type or campaign_format or label:
            return ' '.join([campaign_type, campaign_format, label])
        return ''


class OfferLabel(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = _('Offer Label')
        verbose_name_plural = _('Offer Labels')
        ordering = ['pk']

    def __str__(self):
        return self.name


OFFER_TYPE = (
    (1, 'Single Step'),
    (2, '2 Step'),
)
class Offer(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    label = models.ForeignKey(OfferLabel, on_delete=models.CASCADE)
    type = models.IntegerField(choices=OFFER_TYPE, default=1)
    s1_payout = models.IntegerField()
    s2_payout = models.IntegerField(null=True, blank=True)
    step1 = models.ManyToManyField(LabelCampaign, related_name='offer_step1')
    step2 = models.ManyToManyField(LabelCampaign, related_name='offer_step2')
    step1_prepaids = models.ManyToManyField(LabelCampaign, related_name='offer_step1_prepaids')
    step2_prepaids = models.ManyToManyField(LabelCampaign, related_name='offer_step2_prepaids')
    step1_tablet = models.ManyToManyField(LabelCampaign, related_name='offer_step1_tablet', blank=True)
    step2_tablet = models.ManyToManyField(LabelCampaign, related_name='offer_step2_tablet', blank=True)

    class Meta:
        verbose_name = _('Offer')
        verbose_name_plural = _('Offers')
        ordering = ['pk']

    def __str__(self):
        return self.name + ' - ' + self.crm.crm_name + '(' + str(self.crm.sales_goal) + ')'


class Affiliate(models.Model):
    name = models.CharField(max_length=128)
    afid = models.CharField(max_length=128)
    code = models.CharField(max_length=16, null=True, blank=True)
    bot = models.CharField(max_length=16, null=True, blank=True)

    class Meta:
        verbose_name = _('Affiliate')
        verbose_name_plural = _('Affiliates')
        ordering = ['pk']

    def __str__(self):
        return self.name + ' - ' + self.afid


class AffiliateOffer(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    goal = models.IntegerField()
    s1_payout = models.IntegerField(null=True, blank=True)
    s2_payout = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Affiliate Offer')
        verbose_name_plural = _('Affiliate Offers')
        ordering = ['affiliate', 'pk']

    def __str__(self):
        return self.affiliate.name + ' - ' + self.offer.name


class ResultBase(models.Model):
    from_date = models.DateField()
    to_date = models.DateField()
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    result = models.TextField()

    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        ordering = ['pk']
        abstract = True

    def __str__(self):
        return str(self.from_date) + '~' + str(self.to_date) + ', ' + self.crm.crm_name


class InitialResult(ResultBase):
    class Meta:
        verbose_name = _('Initial Result')
        verbose_name_plural = _('Initial Results')


class Rebill(models.Model):
    crm = models.ForeignKey(CrmAccount, on_delete=models.CASCADE)
    rebills = models.ManyToManyField(LabelCampaign, related_name='rebill')

    class Meta:
        verbose_name = _('Rebill List')
        verbose_name_plural = _('Rebill List')
        ordering = ['pk']

    def __str__(self):
        return str(self.crm.crm_name)


class RebillResult(ResultBase):
    class Meta:
        verbose_name = _('Rebill Result')
        verbose_name_plural = _('Rebill Results')


class CapUpdateResult(ResultBase):
    class Meta:
        verbose_name = _('Cap Update Result')
        verbose_name_plural = _('Cap Update Results')


class OfferBilling(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    trial_desktop = models.ForeignKey(LabelCampaign, related_name='offer_desktop_trial', on_delete=models.CASCADE)
    trial_mobile = models.ForeignKey(LabelCampaign, related_name='offer_mobile_trial', on_delete=models.CASCADE)
    mc_desktop = models.ForeignKey(LabelCampaign, related_name='offer_desktop_mc', on_delete=models.CASCADE)
    mc_mobile = models.ForeignKey(LabelCampaign, related_name='offer_mobile_mc', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Billing Offer')
        verbose_name_plural = _('Offers of Billing')
        ordering = ['pk']

    def __str__(self):
        return self.offer.name + '(' + self.offer.crm.crm_name + ')'


class BillingAffiliate(models.Model):
    name = models.CharField(max_length=128)
    afid = models.CharField(max_length=128)

    class Meta:
        verbose_name = _('Billing Affiliate')
        verbose_name_plural = _('Affiliates of Billing')
        ordering = ['pk']

    def __str__(self):
        return '%s - %s' % (self.name, self.afid)


class BillingResult(models.Model):
    from_date = models.DateField()
    to_date = models.DateField()
    billing = models.ForeignKey(OfferBilling, on_delete=models.CASCADE)
    trial_result = models.TextField()
    mc_result = models.TextField()

    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        ordering = ['pk']
        verbose_name = _('Billing Result')
        verbose_name_plural = _('Billing Results')

    def __str__(self):
        return str(self.from_date) + '~' + str(self.to_date) + ', ' + self.billing.offer.name
