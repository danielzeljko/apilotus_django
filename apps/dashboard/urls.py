from django.conf.urls import url
from dashboard import views


urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
]
