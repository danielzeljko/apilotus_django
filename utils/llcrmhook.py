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
        self.retention_url = (self.crm_url + '/admin/report/custom/index.php?r=8&test_flag=0&from_date={}&to_date={}&rebill_depth={}&aff={}').format

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
        retentions = self.get_retention_report(from_date, to_date, 1)

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
        headers = {
            'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token,
        }
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

    def get_retention_report(self, from_date, to_date, cycle=1):
        headers = {
            'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token,
            'referer': self.crm_url + '/admin/report/custom/index.php?r=8',
        }
        response = requests.get(self.retention_url(from_date, to_date, cycle, 0), headers=headers)
        if str(response.text).__contains__('No results exist at this time.'):
            return []
        data = fromstring(response.text)

        cycle_count = data.xpath('//div[@class="list-data"]/table/tr[1]/td/text()')
        if 2 == cycle and len(cycle_count) == 2:
            cycle_count = 2
        else:
            cycle_count = 1

        retentions = data.xpath('//div[@class="list-data"]/table/tr')[2:-1]
        results = []
        for retention in retentions:
            campaign_id = retention.xpath('.//td[1]/text()')[0].split(')')[0][1:]
            data = {
                'campaign_id': int(self.parse_value(campaign_id)),
                'campaign_name': retention.xpath('.//td[1]/text()')[0].replace('(' + campaign_id + ')', '').strip(),
                'gross_orders': int(self.parse_value(retention.xpath('.//td[2]/text()')[0])),
                'net_approved': int(self.parse_value(retention.xpath('.//td[3]/text()')[0])),
                'subscriptions_approved': int(self.parse_value(retention.xpath('.//td[4]/text()')[0])),
                'declined': int(self.parse_value(retention.xpath('.//td[5]/text()')[0])),
                'void_full_refund': int(self.parse_value(retention.xpath('.//td[6]/text()')[0])),
                'partial_refund': int(self.parse_value(retention.xpath('.//td[7]/text()')[0])),
                'void_refund_revenue': float(self.parse_value(retention.xpath('.//td[8]/text()')[0])),
                'canceled': int(self.parse_value(retention.xpath('.//td[9]/text()')[0])),
                'hold': int(self.parse_value(retention.xpath('.//td[10]/text()')[0])),
                'pending': int(self.parse_value(retention.xpath('.//td[11]/text()')[0])),
                'approval_rate': float(self.parse_value(retention.xpath('.//td[12]/text()')[0])),
                'net_revenue': float(self.parse_value(retention.xpath('.//td[13]/text()')[0])),
            }
            if 1 == cycle_count:
                data['has_affiliate'] = True if retention.xpath('.//td[14]/.//a/text()') else False
            else:
                data['gross_orders1'] = int(self.parse_value(retention.xpath('.//td[14]/text()')[0]))
                data['net_approved1'] = int(self.parse_value(retention.xpath('.//td[15]/text()')[0]))
                data['declined1'] = int(self.parse_value(retention.xpath('.//td[16]/text()')[0]))
                data['void_full_refund1'] = int(self.parse_value(retention.xpath('.//td[17]/text()')[0]))
                data['partial_refund1'] = int(self.parse_value(retention.xpath('.//td[18]/text()')[0]))
                data['void_refund_revenue1'] = float(self.parse_value(retention.xpath('.//td[19]/text()')[0]))
                data['canceled1'] = int(self.parse_value(retention.xpath('.//td[20]/text()')[0]))
                data['hold1'] = int(self.parse_value(retention.xpath('.//td[21]/text()')[0]))
                data['pending1'] = int(self.parse_value(retention.xpath('.//td[22]/text()')[0]))
                data['approval_rate1'] = float(self.parse_value(retention.xpath('.//td[23]/text()')[0]))
                data['net_revenue1'] = float(self.parse_value(retention.xpath('.//td[24]/text()')[0]))
                data['has_affiliate'] = True if retention.xpath('.//td[25]/.//a/text()') else False
            results.append(data)
        return results

    def get_retention_report_by_campaign(self, from_date, to_date, cycle, campaign_id):
        headers = {
            'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token,
            'referer': self.crm_url + '/admin/report/custom/index.php?r=8',
        }
        response = requests.get(self.retention_url(from_date, to_date, cycle, 1) + '&f=' + str(campaign_id), headers=headers)
        if str(response.text).__contains__('No results exist at this time.'):
            return []
        data = fromstring(response.text)
        retentions = data.xpath('//div[@class="list-data"]/table/tr')[2:-1]
        results = []
        for retention in retentions:
            results.append({
                'affiliate_id': retention.xpath('.//td[1]/text()')[0],
                'affiliate_name': '',   # ??? priamry_label_affiliate(affiliate_id, crm_id, label, sales_goal)
                'gross_orders': int(self.parse_value(retention.xpath('.//td[2]/text()')[0])),
                'net_approved': int(self.parse_value(retention.xpath('.//td[3]/text()')[0])),
                'subscriptions_approved': int(self.parse_value(retention.xpath('.//td[4]/text()')[0])),
                'declined': int(self.parse_value(retention.xpath('.//td[5]/text()')[0])),
                'void_full_refund': int(self.parse_value(retention.xpath('.//td[6]/text()')[0])),
                'partial_refund': int(self.parse_value(retention.xpath('.//td[7]/text()')[0])),
                'void_refund_revenue': float(self.parse_value(retention.xpath('.//td[8]/text()')[0])),
                'canceled': int(self.parse_value(retention.xpath('.//td[9]/text()')[0])),
                'hold': int(self.parse_value(retention.xpath('.//td[10]/text()')[0])),
                'pending': int(self.parse_value(retention.xpath('.//td[11]/text()')[0])),
                'approval_rate': float(self.parse_value(retention.xpath('.//td[12]/text()')[0])),
                'net_revenue': float(self.parse_value(retention.xpath('.//td[13]/text()')[0])),
                'has_sub_affiliate': True if retention.xpath('.//td[14]/.//a/text()') else False,
            })
        return results

    def get_retention_report_by_affiliate(self, from_date, to_date, cycle, campaign_id, affiliate_id):
        headers = {
            'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token,
            'referer': self.crm_url + '/admin/report/custom/index.php?r=8&aff=1&f=' + str(campaign_id),
        }
        response = requests.get(self.retention_url(from_date, to_date, cycle, 1) + '&f=' + str(campaign_id) + '&sf=AFFID:' + str(affiliate_id), headers=headers)
        if str(response.text).__contains__('No results exist at this time.'):
            return []
        data = fromstring(response.text)
        retentions = data.xpath('//div[@class="list-data"]/table/tr')[2:-1]
        results = []
        for retention in retentions:
            results.append({
                'sub_affiliate_name': retention.xpath('.//td[1]/text()')[0],
                'gross_orders': int(self.parse_value(retention.xpath('.//td[2]/text()')[0])),
                'net_approved': int(self.parse_value(retention.xpath('.//td[3]/text()')[0])),
                'subscriptions_approved': int(self.parse_value(retention.xpath('.//td[4]/text()')[0])),
                'declined': int(self.parse_value(retention.xpath('.//td[5]/text()')[0])),
                'void_full_refund': int(self.parse_value(retention.xpath('.//td[6]/text()')[0])),
                'partial_refund': int(self.parse_value(retention.xpath('.//td[7]/text()')[0])),
                'void_refund_revenue': float(self.parse_value(retention.xpath('.//td[8]/text()')[0])),
                'canceled': int(self.parse_value(retention.xpath('.//td[9]/text()')[0])),
                'hold': int(self.parse_value(retention.xpath('.//td[10]/text()')[0])),
                'pending': int(self.parse_value(retention.xpath('.//td[11]/text()')[0])),
                'approval_rate': float(self.parse_value(retention.xpath('.//td[12]/text()')[0])),
                'net_revenue': float(self.parse_value(retention.xpath('.//td[13]/text()')[0])),
            })
        return results

    def get_sales_report_for_cap_update(self, from_date, to_date, campaign_id, aff, f, sf):
        headers = {
            'cookie': 'p_cookie=1; o_cookie=1; c_cookie=1; b_cookie=1; ' + self.token,
        }

        url = self.prospect_url(from_date, to_date)
        if aff:
            if campaign_id:
                url += '&affiliate_id=' + campaign_id
            url += '&aff=' + aff
            if f:
                url += '&f=' + f
            if sf:
                url += '&sf=' + sf
        else:
            if campaign_id:
                url += '&campaign_id=' + campaign_id

        response = requests.get(url, headers=headers)
        if response.text.__contains__('No results exist at this time.'):
            return []
        data = fromstring(response.text)

        prospects = data.xpath('//table[@class="list "]/tr')

        page_type = prospects[0].xpath('.//td[1]/span/text()')[0]

        results = []
        for prospect in prospects[1:]:
            total = prospect.xpath('.//td[1]/b/text()')
            if total:
                id = 'Total'
            else:
                if page_type == 'Campaign Name':
                    id = self.parse_value(prospect.xpath('.//td[1]/text()')[0].split(')')[0][1:])
                    if not id:
                        id = self.parse_value(prospect.xpath('.//td[1]/@title')[0].split(')')[0][1:])
                else:
                    id = prospect.xpath('.//td[1]/text()')[0]
            data = {
                'id': id,
                'prospects': int(self.parse_value(prospect.xpath('.//td[2]/text()')[0])),
                'initial_customers': int(self.parse_value(prospect.xpath('.//td[3]/text()')[0])),
                'conversion_rate': float(self.parse_value(prospect.xpath('.//td[4]/text()')[0])),
                'gross_revenue': float(self.parse_value(prospect.xpath('.//td[5]/text()')[0])),
                'average_revenue': float(self.parse_value(prospect.xpath('.//td[6]/text()')[0])),
            }
            if total:
                affiliate_breakdown = prospect.xpath('.//td[7]/a/@onclick')
            else:
                affiliate_breakdown = prospect.xpath('.//td[7]/div/div/a/@onclick')
            if affiliate_breakdown:
                data['search_affiliate'] = affiliate_breakdown[0].split(',')[1].replace("'", '')
                data['has_affid'] = affiliate_breakdown[0].split(',')[2].replace("'", '').replace(')', '')
                if page_type == 'Campaign Name':
                    data['sub_affid'] = 'Affiliate'
                else:
                    data['sub_affid'] = 'Sub-Affiliate'
            else:
                data['search_affiliate'] = ''
                data['has_affid'] = ''
                data['sub_affid'] = ''

            results.append(data)

        return results

    def parse_value(self, value):
        return value.replace('%', '').replace('$', '').replace(',', '')
