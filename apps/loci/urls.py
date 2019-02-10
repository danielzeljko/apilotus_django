from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^places/ajax/search',
        views.places_ajax_search, name='loci_places_ajax_search'),
    ]