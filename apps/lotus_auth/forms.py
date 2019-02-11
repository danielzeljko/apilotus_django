import datetime
import string
import logging
import re

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    ReadOnlyPasswordHashField,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm
)
from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings

from lotus_auth.models import LotusUser

logger = logging.getLogger("apps.{}".format(__name__))
STRONG_PASS_RE = re.compile(r"(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[_!@#$%^&*-+=/?> . , ; :'()<])")
STRONG_PASS_MSG = "Password requirements: 8 characters, 1 lowercase letter, 1 uppercase letter, 1 number, 1 special character."
MEDIUM_PASS_RE = re.compile(r"(?=.{8,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9])))")
MEDIUM_PASS_MSG = "Password requirements: must have either capitals and lowercase letters or lowercase and numbers."
MUSIC_TESTING_CONFIRMATION_MSG = "To continue, you must accept the Terms and Conditions"
I_ACCEPT_TERMS_LABEL = "I Accept the Terms and Conditions."


class LotusAuthenticationForm(AuthenticationForm):

    def clean(self):

        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username or not password:
            raise forms.ValidationError("Must enter username and password.")
        if '@' in username:  # using email to login
            try:
                user_with_email = LotusUser.objects.filter(email__iexact=username).first()
                if not user_with_email:
                    raise LotusUser.DoesNotExist()
                self.cleaned_data['username'] = user_with_email.username
                username = user_with_email.username
            except LotusUser.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['invalid_email'],
                    code='invalid_email',
                    params={'username': self.username_field.verbose_name},
                )
            except Exception as e:
                logger.error("There was an error with cleaning user name {}: {}".format(username, e))
        else:  # using username to login
            try:
                username_user = LotusUser.objects.filter(username__iexact=username).first()
                if not username_user:
                    raise LotusUser.DoesNotExist()
            except LotusUser.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['invalid_username'],
                    code='invalid_username',
                    params={'username': self.username_field.verbose_name},
                )
            except Exception as e:
                logger.error("There was an error with cleaning user name {}: {}".format(username, e))

        # AllowAllUsersModelBackend allows inactive users auth
        self.user_cache = AllowAllUsersModelBackend().authenticate(self.origreq, username=username, password=password)

        if self.user_cache is None:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name},
            )
        elif not self.user_cache.is_active:
            self.inactive_user = True
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

        return self.cleaned_data

    def __init__(self, request=None, *args, **kwargs):

        self.origreq = request or kwargs.get('request')

        super(LotusAuthenticationForm, self).__init__(*args, **kwargs)

        # Django automatically adds an auto focus to
        # Username on the auth form
        if self.origreq.is_ajax():
            self.fields['username'].widget.attrs.pop('autofocus')

        self.current_site = Site.objects.get_current(self.origreq)

        self.error_messages = {
            'invalid_login': (
                "Your password didn't match with your account in our system. Please try again."
            ),
            'inactive': (
                "Your account is not active. Please contact webmaster@"+self.current_site.domain+"."
            ),
            'invalid_email': (
                "Your email didn't match with an account in our system. Please try again or create an account."
            ),
            'invalid_username': (
                "Your username didn't match with an account in our system. Please try again or create an account."
            ),
            'awaiting_musictesting_confirmation': (
                "The site Terms and Conditions have been updated. Please acknowledge the new terms to continue."
            ),
        }
