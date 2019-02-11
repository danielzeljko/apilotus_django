from django.conf.urls import url
from lotus_auth import forms
from django.contrib.auth import views as django_auth_views
from lotus_auth import views as lotus_auth_views


urlpatterns = [
    # MWC Custom Auth Views
    url(r'^login/$',
        lotus_auth_views.login, {
            'template_name': 'lotus_auth/login.html',
            'authentication_form': forms.LotusAuthenticationForm
        }, name='account_login'),
]
