import random
import csv
import calendar

from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.shortcuts import get_current_site

from django.core.mail import EmailMessage
from django.urls import reverse
from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import (
    login as django_auth_login,  # to prevent confusion with the local `login`
    get_user_model,
    logout as django_auth_logout,
    REDIRECT_FIELD_NAME)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login as auth_login_view
from django.contrib import messages
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext as _
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.template.response import TemplateResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

# from el_pagination.decorators import page_template
# from ipwhois import Net
# from ipwhois.asn import IPASN

# from broadcast.models import Station
# from mailchimp.client import MailChimpClient
from lotus_auth.forms import *
from lotus_auth.models import LotusUserSignup, LotusUser

# from simple_contesting.utils import generate_stats_by_users
# from site_personas.utils import is_brand_manager

# from radiocms.decorators import *
# from radiocms import constants as c
# from radiocms.utils import get_client_ip, validate_invisible_recaptcha, get_google_recaptcha_site_key

logger = logging.getLogger("apps.{}".format(__name__))


def _get_login_redirect_url(request, redirect_to):
    # Ensure the user-originating redirection URL is safe.
    if not is_safe_url(url=redirect_to, allowed_hosts=request.get_host()):
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    return redirect_to


@sensitive_post_parameters()
@never_cache
def login(request, template_name='lotus_auth/login.html', redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=LotusAuthenticationForm, redirect_authenticated_user=True):
    # Stealing parts of login view in Django 1.9 so we can redirect

    current_site = get_current_site(request)

    redirect_to = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name, ''))

    if redirect_authenticated_user and request.user.is_authenticated:
        redirect_to = _get_login_redirect_url(request, redirect_to)
        if redirect_to == request.path:
            raise ValueError(
                "Redirection loop for authenticated user detected. Check that "
                "your LOGIN_REDIRECT_URL doesn't point to a login page."
            )
        return HttpResponseRedirect(redirect_to)

    elif request.method == "POST":
        form = authentication_form(data=request.POST, request=request)
        if form.is_valid():
            # auth_login_view(request, template_name=template_name, authentication_form=authentication_form)
            user = LotusUser.objects.get(username=form.cleaned_data['username'])
            auth_login_view(request, user)

            user.sites_logged.add(current_site)
            user.save()

            next_redirect = _get_login_redirect_url(request, redirect_to)

            return HttpResponseRedirect("{}?nocache=1&authenticationsuccess=1".format(next_redirect))
    else:
        form = authentication_form(request=request)

        # save for redirect after account activation from email
        next_after_activation = request.GET.get('next')
        request.session['next_after_activation'] = next_after_activation

    # display resent activation form if user requested so.
    send_activation_code = request.GET.get('send_activation_code')

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'login_page': True,
        'send_activation_code': send_activation_code
    }

    return TemplateResponse(request, template_name, context)
