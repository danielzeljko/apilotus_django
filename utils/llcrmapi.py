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


# crm_accounts = [
#     ['https://falcor.limelightcrm.com', 'api-tool2', 'Wwk8v3GPwCJhkM'],
#     ['https://ebrandsoffers.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://securesystem.limelightcrm.com', 'api-tool2', 'yAFN4AuVCXzqgH'],
#     ['https://balance.limelightcrm.com', 'api-tool2', 'u9tT58A2sJeRve'],
#     ['https://mmsales.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://malibu.limelightcrm.com', 'trafficapi', 'nMtsTjH5gC7Jb'],
#     ['https://corecrm.limelightcrm.com', 'api-tool2', 'vEpRGJZgbYJZpJ'],
#     ['https://poswebsol.limelightcrm.com', 'api-tool2', '6xX4hTcWCapNQ'],
#     ['https://digitalaud.limelightcrm.com', 'api-tool2', 'z4FWdqhaa7rAFt'],
#     ['https://circlecomm.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://buyid.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://smoneyoffers.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://xldnet.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://vantage.limelightcrm.com', 'trafficapi', '6xX4hTcWCapNQ'],
#     ['https://tecsky.limelightcrm.com', 'api-tool2', '4WYTdU75yhsWfY'],
# ]
#
# for crm in crm_accounts:
#     llcrm_api = LLCRMAPI(crm[0], crm[1], crm[2])
#     campaigns = llcrm_api.campaigns()
#     if campaigns['response_code'] != "100":
#         print(crm[0], campaigns['response_code'])
#     else:
#         print(crm[0], campaigns['response_code'], campaigns['campaigns'])
