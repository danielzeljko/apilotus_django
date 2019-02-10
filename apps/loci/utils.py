import json
import codecs
import requests

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.contrib.sites.shortcuts import get_current_site


def _geo_query(query, query_type=None):

    try:
        query = u"%s" % query
    except Exception:
        pass

    if type(query) is unicode:
        query = codecs.encode(query, 'ascii', 'ignore')
    cache_key = 'geo:' + slugify(str(query))
    location_data = cache.get(cache_key)

    if not location_data:

        # All Google API response data
        data = {}
        # API resul containing geometry data
        result = {}
        street_address = city = state = zip_code = None
        number = route = ''

        # Call Google API
        api_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

        google_map_key = getattr(settings, 'GOOGLE_MAPS_API_KEY_WITH_SERVER_RESTRICTION')
        if google_map_key:
            api_url += 'key={key}&'.format(key=google_map_key)

        if query_type == 'address':
            api_url += 'address=%s' % query
        else:
            api_url += 'latlng=%s,%s' % query
        api_url += '&sensor=false'
        try:
            resp = requests.get(api_url)
        except requests.exceptions.RequestException:
            pass
        else:
            if resp.ok:
                data = json.loads(resp.text)

        # for now, we only need coords and address, but more is available
        results = data.get('results', [])

        if results:
            result = results[0]

        latlon = result.get('geometry', {}).get('location', {})
        location = (latlon.get('lat'), latlon.get('lng'))

        acomps = result.get('address_components', [])
        for comp in acomps:
            if 'street_number' in comp['types']:
                number = comp['long_name']
            if 'route' in comp['types']:
                route = comp['long_name']
            if 'locality' in comp['types']:
                city = comp['long_name']
            if 'administrative_area_level_1' in comp['types']:
                state = comp['short_name']
            if 'postal_code' in comp['types']:
                zip_code = comp['long_name']
        if number or route:
            street_address = number + ' ' + route

        if query_type == 'address' and not (city and state and zip_code) and location != (None, None):
            # missing some data, try to get it from coords
            loc_data = get_geo(location)
            if not city:
                city = loc_data.city
            if not state:
                state = loc_data.state
            if not zip_code:
                zip_code = loc_data.zip_code

        location_data = (location, (street_address, city, state, zip_code))
        if data:
            cache.set(cache_key, location_data, 86400)

    # get the model here to prevent circular import
    place_model = apps.get_model('loci', 'place')

    (location, (address, city, state, zip_code)) = location_data

    return place_model(
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        location=location
    )


def geocode(address):

    return _geo_query(address, query_type='address')


def get_geo(location):
    return _geo_query(location)


def geolocate_request(request, default_dist=None, max_distance_default=80):
    found = False
    geo_query = request.GET.get('geo')
    try:
        found_dist = int(request.GET.get('dist', ''))
    except ValueError:
        found_dist = request.session.get('geodistance', default_dist or max_distance_default)
    if geo_query:
        # if the user has submitted an address, attempt to look it up
        geolocation = geocode(geo_query)
        if geolocation.latitude is not None:
            # # geolocation found from address, save the query only
            # # lookup data should be cached, so no need to save it in session
            request.session['geolocation'] = geo_query
            # request.session['geodistance'] = found_dist
            found = True
    if not found and request.session.get('geolocation'):
        # there is an existing geo_query in the session
        geolocation = geocode(request.session['geolocation'])
        if geolocation.latitude is not None:
            found = True
        # else:
        #     # the query did not find anything, remove it from the session
        #     del request.session['geodistance']
            del request.session['geolocation']
    if not found:
        # could not otherwise find location data, fall back to station ZIP code
        try:
            zip_code = get_current_site(request).profile.zip_code
        except AttributeError:
            zip_code = settings.DEFAULT_ZIP_CODE
        defloc = geocode(zip_code)
        geolocation = defloc
    if found:
        geolocation.nearby_distance = found_dist
    else:
        geolocation.nearby_distance = max_distance_default
    return geolocation
