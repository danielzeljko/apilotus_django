import datetime

from django.conf import settings
from django.contrib import auth
from django.contrib.sites.models import Site

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, User, Group, Permission, _user_has_perm, _user_get_all_permissions, _user_has_module_perms

from localflavor.us.us_states import STATE_CHOICES
from loci.utils import geocode
from lotus_dashboard.models import CrmAccount


class LotusUserManager(BaseUserManager):

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        # email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)

    def valid(self, **kwargs):
        """
        Returns profile objects with an age at or above the minimum age.
        """
        current = timezone.now().date()
        min_date = datetime.date(current.year - getattr(settings, 'MINIMUM_USER_AGE', 13), current.month, current.day)
        return self.filter(date_of_birth__lte=min_date)


class LotusUser(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=100)

    sms = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True, null=True, blank=True)
    bot = models.CharField(max_length=100, null=True, blank=True)
    sms_enable = models.BooleanField(default=False)
    email_enable = models.BooleanField(default=False)
    bot_enable = models.BooleanField(default=False)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=6,
        choices=[("male", "Male"), ("female", "Female")],
        null=True, blank=True
    )

    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATE_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    county = models.CharField(max_length=100, blank=True, null=True)

    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)
    site_joined = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE)
    sites_logged = models.ManyToManyField(
        Site, blank=True, related_name='users_logged'
    )

    groups = models.ManyToManyField(Group, blank=True)
    user_permissions = models.ManyToManyField(Permission, blank=True)
    crm_permissions = models.ManyToManyField(CrmAccount, blank=True)
    crm_positions = models.CharField(max_length=100, null=True, blank=True)
    page_permissions = models.CharField(max_length=100, null=True, blank=True)

    user_status = models.IntegerField(blank=False, default=1)
    user_role = models.CharField(
        max_length=5,
        choices=[("admin", "Admin"), ("user", "User")],
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # languages_spoken = models.ManyToManyField(Language, blank=True)

    sites_subscribed = models.ManyToManyField(Site, blank=True, related_name='subscribed_users')

    # Google Analytics User-ID opt-out flag. This is required by the Google's User-ID Policy.
    # See https://support.google.com/analytics/answer/3123666
    # is_opt_out_user_id_tracking = models.BooleanField(default=False)
    # signup_ip_address = models.GenericIPAddressField(default='127.0.0.1')
    # signup_country_code = models.CharField(max_length=10, blank=True)

    objects = LotusUserManager()

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['date_of_birth', 'first_name', 'address', 'city', 'zipcode', 'last_name', 'gender']

    def is_male(self):
        return self.gender == 'male'

    @property
    def profile(self):
        return self

    def get_full_name(self):
        return u"{} {}".format(self.first_name.strip(), self.last_name.strip())

    def get_short_name(self):
        return self.username

    def get_age(self):
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def age(self):
        return self.get_age()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)

    def set_geocode(self):
        if self.address and self.city and self.state:
            # "or ''" is required to avoid "None"
            addr = u"{} {}, {} {}".format(
                self.address or '',
                self.city or '',
                self.state or '',
                self.zipcode or ''
            ).encode('utf-8')
            place = geocode(addr)
            if place.latitude and place.longitude:
                self.latitude = place.latitude
                self.longitude = place.longitude

    def is_subscribed_to_current_site(self, current_site):
        """
        Returns True if user is subscribed to current site

        """
        return current_site in self.sites_subscribed.all()

    def is_site_manager(self, current_site):

        return current_site.profile.managers.filter(
            username=self.username,
            is_active=True
        ).exists()

    def is_super(self):
        return self.is_active and self.is_superuser

    def save(self, *args, **kwargs):
        self.set_geocode()
        if getattr(self, 'last_login') is None:
            self.last_login = timezone.now()
        super(AbstractBaseUser, self).save(*args, **kwargs)

    # user notification table filter
    def get_notifications(self):
        args = (Q(notice_type__expire_at__isnull=True) | Q(notice_type__expire_at__gte=timezone.now()),)
        kwargs = dict(deleted=False)
        return self.notification_set.filter(*args, **kwargs)

    def unseen_notification_count(self):
        notifications = self.get_notifications()
        return notifications.filter(seen_at__isnull=True).count()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['pk']


class LotusUserSignup(models.Model):
    user = models.ForeignKey(LotusUser, on_delete=models.CASCADE)
    confirmation_string = models.CharField(max_length=20)
    completed = models.BooleanField(default=False)
    pwhash = models.CharField(max_length=256)
    datetime = models.DateTimeField(default=timezone.now)
