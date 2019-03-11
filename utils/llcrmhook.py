import requests
from django.utils import timezone
from lotus_dashboard.models import *
from lxml.html import fromstring


class LLCRMHook(object):
    def __init__(self, crm_id):
        self.crm_id = crm_id
        crm = CrmAccount.objects.get(pk=crm_id)
        self.crm_url = crm.crm_url
        self.username = crm.username
        self.password = crm.password
        self.token = ''

        self.prospect_url = (self.crm_url + '/admin/report/custom/index.php?r=7&test_flag=0&from_date={}&to_date={}').format
        self.retention_url = (self.crm_url + '/admin/report/custom/index.php?r=8&test_flag=0&from_date={}&to_date={}&rebill_depth={}&aff=0').format

        self.login()

    def login(self):
        try:
            token = CrmToken.objects.get(crm_id=self.crm_id)
            if (timezone.now() - token.timestamp).seconds < 1440:   # expired token
                token.save()
                self.token = token.token
                return
        except CrmToken.DoesNotExist:
            token = CrmToken(crm_id=self.crm_id)

        headers = {
            'origin': self.crm_url,
            'referer': self.crm_url + '/admin/login.php',
        }
        data = {
            'login_url': '',
            'securityToken': '',
            'admin_name': self.username,
            'admin_pass': self.password,
        }
        response = requests.post(self.crm_url + '/admin/login.php', headers=headers, data=data)
        new_token = response.headers['set-cookie'].split(';')[0]
        token.token = new_token
        token.save()
        self.token = new_token

    def get_crm_sales(self, from_date, to_date):
        prospects = self.get_prospect_report(from_date, to_date)
        retentions, cycle = self.get_retention_report(from_date, to_date, 1)

        campaign_step1 = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=1)
        campaign_step2 = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=2)
        campaign_prepaids = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=3)
        campaign_prepaids_step1 = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=3).filter(campaign_format=1)
        campaign_prepaids_step2 = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=3).filter(campaign_format=2)
        campaign_tablet_step1 = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=4).filter(campaign_format=1)
        campaign_tablet_step2 = LabelCampaign.objects.filter(crm_id=self.crm_id).filter(campaign_type=4).filter(campaign_format=2)

        label_info = LabelGoal.objects.filter(crm_id=self.crm_id).filter(visible=True)
        results = [{
            'label_id': None,
            'label_goal': 0,
            'step1': 0,
            'step2': 0,
            'step1_nonpp': 0,
            'step2_nonpp': 0,
            'prepaids': 0,
            'prepaids_step1': 0,
            'prepaids_step2': 0,
            'tablet_step1': 0,
            'tablet_step2': 0,
            'order_count': 0,
            'order_page': 0.0,
            'declined': 0,
            'gross_order': 0,
        }]
        for label_goal in label_info:
            results.append({
                'label_id': label_goal.label.id,
                'label_goal': label_goal.goal,
                'step1': 0,
                'step2': 0,
                'step1_nonpp': 0,
                'step2_nonpp': 0,
                'prepaids': 0,
                'prepaids_step1': 0,
                'prepaids_step2': 0,
                'tablet_step1': 0,
                'tablet_step2': 0,
                'order_count': 0,
                'order_page': 0.0,
                'declined': 0,
                'gross_order': 0,
            })

        for prospect in prospects:
            for item in campaign_step1:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['step1'] += prospect['initial_customer']
                    results[0]['step1_nonpp'] += prospect['initial_customer']
                    results[0]['order_count'] += 1
                    results[0]['order_page'] += prospect['conversion_rate']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['step1'] += prospect['initial_customer']
                            results[idx + 1]['step1_nonpp'] += prospect['initial_customer']
                            results[idx + 1]['order_page'] += prospect['conversion_rate']
                            results[idx + 1]['order_count'] += 1
            for item in campaign_step2:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['step2'] += prospect['initial_customer']
                    results[0]['step2_nonpp'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['step2'] += prospect['initial_customer']
                            results[idx + 1]['step2_nonpp'] += prospect['initial_customer']
            for item in campaign_prepaids:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['prepaids'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['prepaids'] += prospect['initial_customer']
            for item in campaign_prepaids_step1:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['prepaids_step1'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['prepaids_step1'] += prospect['initial_customer']
            for item in campaign_prepaids_step2:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['prepaids_step2'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['prepaids_step2'] += prospect['initial_customer']
            for item in campaign_tablet_step1:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['tablet_step1'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['tablet_step1'] += prospect['initial_customer']
            for item in campaign_tablet_step2:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['tablet_step2'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['tablet_step2'] += prospect['initial_customer']

        for retention in retentions:
            for item in campaign_step1:
                if item.campaign_id == retention['campaign_id']:
                    results[0]['declined'] += retention['declined']
                    results[0]['gross_order'] += retention['gross_orders']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['declined'] += retention['declined']
                            results[idx + 1]['gross_order'] += retention['gross_orders']

        return results

    def get_prospect_report(self, from_date, to_date):
        headers = {'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token}
        response = requests.get(self.prospect_url(from_date, to_date), headers=headers)
        data = fromstring(response.text)
        prospects = data.xpath('//table[@class="list "]/tr')[1:-1]
        results = []
        for prospect in prospects:
            campaign_id = self.parse_value(prospect.xpath('.//td[1]/text()')[0].split(')')[0][1:])
            if not campaign_id:
                campaign_id = self.parse_value(prospect.xpath('.//td[1]/@title')[0].split(')')[0][1:])
            campaign_id = int(campaign_id)
            try:
                label_campaign = LabelCampaign.objects.get(crm_id=self.crm_id, campaign_id=campaign_id)
                if label_campaign.campaign_label:
                    results.append({
                        'campaign_id': campaign_id,
                        'initial_customer': int(self.parse_value(prospect.xpath('.//td[3]/text()')[0])),
                        'conversion_rate': float(self.parse_value(prospect.xpath('.//td[4]/text()')[0])),
                    })
            except LabelCampaign.DoesNotExist:
                pass

        return results

    def get_retention_report(self, from_date, to_date, cycle):
        headers = {
            'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token,
            'referer': self.crm_url + '/admin/report/custom/index.php?r=8',
        }
        response = requests.get(self.retention_url(from_date, to_date, cycle), headers=headers)
        if str(response.text).__contains__('No results exist at this time.'):
            return [], 0
        data = fromstring(response.text)
        retentions = data.xpath('//div[@class="list-data"]/table/tr')[2:-1]
        results = []
        for retention in retentions:
            results.append({
                'campaign_id': int(self.parse_value(retention.xpath('.//td[1]/text()')[0].split(')')[0][1:])),
                'campaign_name': retention.xpath('.//td[1]/text()')[0].split(')')[1].strip(),
                'gross_orders': int(self.parse_value(retention.xpath('.//td[2]/text()')[0])),
                'net_approved': int(self.parse_value(retention.xpath('.//td[3]/text()')[0])),
                'void_full_refund': int(self.parse_value(retention.xpath('.//td[6]/text()')[0])),
                'partial_refund': int(self.parse_value(retention.xpath('.//td[7]/text()')[0])),
                'void_refund_revenue': float(self.parse_value(retention.xpath('.//td[8]/text()')[0])),
                'approval_rate': float(self.parse_value(retention.xpath('.//td[12]/text()')[0])),
                'has_affiliate': True if retention.xpath('.//td[14]/.//a/text()') else False,
                'declined': int(self.parse_value(retention.xpath('.//td[5]/text()')[0])),
            })
        return results, 1

    def parse_value(self, value):
        return value.replace('%', '').replace('$', '').replace(',', '')
