from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

try:
    User = settings.AUTH_USER_MODEL
except ImportError:
    from django.contrib.auth.models import User


def default_expire_time():
    return timezone.now() + timedelta(days=7)


class NoticeType(models.Model):
    """
    label => used to distinguish similar type of the notice eg: dev_notice, site_update etc
    """
    class Meta:
        verbose_name = "WebUpdateNotice"
        verbose_name_plural = "WebUpdateNotices"

    label = models.CharField(_("label"), max_length=40, null=True, blank=True)
    title = models.CharField(_("Title"), max_length=150)
    description = models.CharField(_("description"), max_length=100)
    url = models.URLField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    target_usergroups = models.ManyToManyField(
        Group,
        blank=True,
        help_text="User groups that a notification is sent to.",
    )

    created_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "{0}-{1}".format(self.label, self.title)

    @property
    def expire(self):
        if self.expire_at:
            return timezone.now() < self.expire_at
        return False


class Notification(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    notice_type = models.ForeignKey(NoticeType, verbose_name=_("notice type"), on_delete=models.CASCADE)
    seen_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    @property
    def seen(self):
        return bool(self.seen_at)

    @classmethod
    def send(cls, notice_type, users):

        notifications = [Notification(notice_type=notice_type, user=u) for u in users]
        Notification.objects.bulk_create(notifications)

    class Meta:
        # Prevent same notifications being sent twice
        unique_together = ('user', 'notice_type')
