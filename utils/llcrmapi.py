import requests
from requests.auth import HTTPBasicAuth
import json


class LLCRMAPI(object):
    def __init__(self, url, username, password):
        self.base_url = url + '/api/v1/'
        self.username = username
        self.password = password

    def api_response(self, endpoint):
        response = requests.request("POST", self.base_url + endpoint, auth=HTTPBasicAuth(self.username, self.password))
        return json.loads(response.text)

    def campaigns(self):
        result = self.api_response('campaign_find_active')
        return result
