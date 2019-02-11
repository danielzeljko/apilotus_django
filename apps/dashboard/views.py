from dashboard.models import *
from django.shortcuts import render


def dashboard(request):
    context = {
        'tab_name': 'Dashboard',
    }
    return render(request, 'dashboard/dashboard.html', context=context)
