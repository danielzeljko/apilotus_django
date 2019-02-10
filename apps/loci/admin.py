from django.contrib import admin

from loci.models import Place


class PlaceAdmin(admin.ModelAdmin):
	search_fields = ['name', 'address', 'latitude', 'longitude']

admin.site.register(Place, PlaceAdmin)
