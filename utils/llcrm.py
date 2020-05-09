import time
import requests
from django.db.models import Q
from lxml.html import fromstring

from django.utils import timezone
from lotus_dashboard.models import *


class LLCRM(object):
    def __init__(self, crm):
        self.crm = crm
        self.crm_url = crm.crm_url
        self.username = crm.username
        self.password = crm.password

        self.subdomain = self.crm_url.split('.')[-3]
        self.login_url = self.crm_url + '/admin/login.php'
        self.prospect_url = self.crm_url + '/admin/reports/index.php?d=Sales+By+Prospects'
        self.retention_url = self.crm_url + '/admin/reports/index.php?d=Sales+By+Retention'

        today = timezone.datetime.now().date()
        week_start = today + timezone.timedelta(-today.weekday())
        tomorrow = today + timezone.timedelta(1)
        self.week_to_date = week_start.strftime("%Y/%m/%d") + ' to ' + tomorrow.strftime("%Y/%m/%d")

        self.token = ''

        self.login()

    def login(self):
        data = {
            'admin_name': self.crm.username,
            'admin_pass': self.crm.password,
        }
        response = requests.post(self.login_url, data=data)
        self.token = response.headers['set-cookie'].split(';')[0]
        if self.token == 'token=deleted':
            pass
        print(self.token)

    def get_product_ids(self):
        label_campaigns = LabelCampaign.objects.filter(crm=self.crm).filter(~Q(pid=None))
        pid = ','.join([a.pid for a in label_campaigns])
        pid = pid.split(',')
        return ','.join(set(pid))

    def get_crm_sales_by_date(self, prospects, retentions):
        campaign_step1 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=1)
        campaign_step2 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=2)
        campaign_prepaids = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=3)
        campaign_prepaids_step1 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=3).filter(
            campaign_format=1)
        campaign_prepaids_step2 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=3).filter(
            campaign_format=2)
        campaign_tablet_step1 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=4).filter(
            campaign_format=1)
        campaign_tablet_step2 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=4).filter(
            campaign_format=2)
        campaign_mc_step1 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=5)
        campaign_mc_step2 = LabelCampaign.objects.filter(crm=self.crm).filter(campaign_type=6)

        label_info = LabelGoal.objects.filter(crm=self.crm).filter(visible=True)

        results = [{
            'label_id': None,
            'label_goal': 0,
            'step1': 0,
            'step2': 0,
            'mc_step1': 0,
            'mc_step2': 0,
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
                'mc_step1': 0,
                'mc_step2': 0,
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
            for item in campaign_mc_step1:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['mc_step1'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['mc_step1'] += prospect['initial_customer']
            for item in campaign_mc_step2:
                if item.campaign_id == prospect['campaign_id']:
                    results[0]['mc_step2'] += prospect['initial_customer']
                    for idx, label_goal in enumerate(label_info):
                        if label_goal.label_id == item.label.id:
                            results[idx + 1]['mc_step2'] += prospect['initial_customer']
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

    def get_crm_sales(self, yesterday=False):
        print(self.get_product_ids())
        prospects, prospects_yesterday, prospects_wtd, today_cap, yesterday_cap, wtd_cap = self.get_prospect_report(yesterday)
        retentions, retentions_yesterday, retentions_wtd = self.get_retention_report(yesterday)

        results = self.get_crm_sales_by_date(prospects, retentions)
        results_yesterday = self.get_crm_sales_by_date(prospects_yesterday, retentions_yesterday)
        results_wtd = self.get_crm_sales_by_date(prospects_wtd, retentions_wtd)

        return results, results_yesterday, results_wtd, today_cap, yesterday_cap, wtd_cap

    def get_prospect_report_by_date(self, date, header):
        start_ms = str(int(timezone.now().timestamp() * 1000))
        # data = '[{"result_maker_id":12842,"merge_result_id":null,"query_id":1083454,"vis_config":{"show_view_names":true,"show_row_numbers":true,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"table_theme":"gray","limit_displayed_rows":false,"type":"table","stacking":"","show_value_labels":false,"label_density":25,"legend_position":"center","x_axis_gridlines":false,"y_axis_gridlines":true,"y_axis_combined":true,"show_y_axis_labels":true,"show_y_axis_ticks":true,"y_axis_tick_density":"default","y_axis_tick_density_custom":5,"show_x_axis_label":true,"show_x_axis_ticks":true,"x_axis_scale":"auto","y_axis_scale_mode":"linear","ordering":"none","show_null_labels":false,"show_totals_labels":false,"show_silhouette":false,"totals_color":"#808080","series_types":{},"series_labels":{"prospect_pdt.campaign_disp":"Campaign","prospect_pdt.count_prospects":"Prospects","prospect_pdt.count_customers":"Initial Customers","prospect_pdt.conversion_percent":"Conversion Rate","prospect_pdt.total_revenue":"Gross Revenue","prospect_pdt.average_revenue":"AOV","prospect_pdt.affiliate_breakdown":"Affiliate Breakdown"},"enable_conditional_formatting":false,"conditional_formatting_ignored_fields":[],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false},"dynamic_fields":null,"sorts":["prospect_pdt.count_prospects desc"],"total":true,"id":1083454,"fill_fields":null,"filters":{"prospect_pdt.date_select":"' + date + '","prospect_pdt.is_test":"0","prospect_pdt.currency_fmt":"","prospect_pdt.campaign":"","prospect_pdt.campaign_disp":"","prospect_pdt.affiliate_id":"","prospect_pdt.sub_affiliate_id":""},"model":"limelight_transactional_reporting","view":"prospect_pdt","client_id":"ZRLmeEziCfjgPfEvGv7W6r","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4088,"elementId":28074,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":1083454,"title":"Sales By Prospects"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}},{"result_maker_id":33747,"merge_result_id":null,"query_id":3166097,"vis_config":{"show_view_names":false,"show_row_numbers":true,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"table_theme":"gray","limit_displayed_rows":false,"type":"table","stacking":"","show_value_labels":false,"label_density":25,"legend_position":"center","x_axis_gridlines":false,"y_axis_gridlines":true,"y_axis_combined":true,"show_y_axis_labels":true,"show_y_axis_ticks":true,"y_axis_tick_density":"default","y_axis_tick_density_custom":5,"show_x_axis_label":true,"show_x_axis_ticks":true,"x_axis_scale":"auto","y_axis_scale_mode":"linear","ordering":"none","show_null_labels":false,"show_totals_labels":false,"show_silhouette":false,"totals_color":"#808080","series_types":{},"series_labels":{"prospect_pdt.campaign_disp":"Campaign","prospect_pdt.count_prospects":"Prospects","prospect_pdt.count_customers":"Initial Customers","prospect_pdt.conversion_percent":"Conversion Rate","prospect_pdt.total_revenue":"Gross Revenue","prospect_pdt.average_revenue":"AOV","prospect_pdt.affiliate_breakdown":"Affiliate Breakdown"},"enable_conditional_formatting":false,"conditional_formatting_ignored_fields":[],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false},"dynamic_fields":null,"sorts":null,"total":true,"id":3166097,"fill_fields":null,"filters":{"prospect_pdt.date_select":"' + date + '","prospect_pdt.is_test":"0","prospect_pdt.currency_fmt":"","prospect_pdt.campaign":"","prospect_pdt.select_dimension":"affiliate^_id","prospect_pdt.select_dimension_2":"sub^_affiliate^_id","prospect_pdt.campaign_disp":"","prospect_pdt.affiliate_id":"","prospect_pdt.sub_affiliate_id":""},"model":"limelight_transactional_reporting","view":"prospect_pdt","client_id":"QpjBy0Js1D9hrrBeyTelol","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4088,"elementId":28076,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":3166097,"title":"Data by Traffic Source"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}}]'
        data = '[{"result_maker_id":12842,"merge_result_id":null,"query_id":1083454,"vis_config":{"show_view_names":true,"show_row_numbers":true,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"table_theme":"gray","limit_displayed_rows":false,"type":"table","stacking":"","show_value_labels":false,"label_density":25,"legend_position":"center","x_axis_gridlines":false,"y_axis_gridlines":true,"y_axis_combined":true,"show_y_axis_labels":true,"show_y_axis_ticks":true,"y_axis_tick_density":"default","y_axis_tick_density_custom":5,"show_x_axis_label":true,"show_x_axis_ticks":true,"x_axis_scale":"auto","y_axis_scale_mode":"linear","ordering":"none","show_null_labels":false,"show_totals_labels":false,"show_silhouette":false,"totals_color":"#808080","series_types":{},"series_labels":{"prospect_pdt.campaign_disp":"Campaign","prospect_pdt.count_prospects":"Prospects","prospect_pdt.count_customers":"Initial Customers","prospect_pdt.conversion_percent":"Conversion Rate","prospect_pdt.total_revenue":"Gross Revenue","prospect_pdt.average_revenue":"AOV","prospect_pdt.affiliate_breakdown":"Affiliate Breakdown"},"enable_conditional_formatting":false,"conditional_formatting_ignored_fields":[],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false},"dynamic_fields":null,"sorts":["prospect_pdt.count_prospects desc"],"total":true,"id":1083454,"fill_fields":null,"filters":{"prospect_pdt.date_select":"' + date + '","prospect_pdt.is_test":"0","prospect_pdt.currency_fmt":"","prospect_pdt.campaign":"","prospect_pdt.campaign_disp":"","prospect_pdt.product_id":"' + self.get_product_ids() + '", "prospect_pdt.affiliate_id":"","prospect_pdt.sub_affiliate_id":""},"model":"limelight_transactional_reporting","view":"prospect_pdt","client_id":"ZRLmeEziCfjgPfEvGv7W6r","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4088,"elementId":28074,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":1083454,"title":"Sales By Prospects"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}}]'
        response = requests.post(self.subdomain + '.analytics.limelightcrm.com/api/internal/queries/multi_run_async', data=data, headers=header)
        task_id_1 = response.json()[0]['query_task_id']
        # task_id_2 = response.json()[1]['query_task_id']

        requests.post(self.subdomain + '.analytics.limelightcrm.com/api/internal/queries/async_long_poll', data='["' + task_id_1 + '"]', headers=header)

        # url = (self.subdomain + ".analytics.limelightcrm.com/api/internal/query_tasks/multi_results?query_task_ids[]={}&query_task_ids[]={}").format
        url = (self.subdomain + ".analytics.limelightcrm.com/api/internal/query_tasks/multi_results?query_task_ids[]={}").format
        # response = requests.get(url(task_id_1, task_id_2), headers=header)
        response = requests.get(url(task_id_1), headers=header)
        result = response.json()

        prospects = result[task_id_1]['data']['data']
        results = []
        cap_results = []
        for prospect in prospects:
            campaign_name = prospect['prospect_pdt.campaign_disp']['value']
            campaign_id = int(campaign_name.split(')')[0][1:])
            try:
                label_campaign = LabelCampaign.objects.get(crm=self.crm, campaign_id=campaign_id)
                if label_campaign.campaign_label and label_campaign.pid:
                    results.append({
                        'campaign_id': campaign_id,
                        'initial_customer': prospect['prospect_pdt.count_customers']['value'],
                        'conversion_rate': prospect['prospect_pdt.conversion_percent']['value'],
                    })
            except LabelCampaign.DoesNotExist:
                pass

            # get cap_update
            url = (self.subdomain + ".analytics.limelightcrm.com/api/internal/models/limelight_transactional_reporting/views/prospect_pdt?fields=prospect_pdt.affiliate_id,prospect_pdt.count_prospects,prospect_pdt.count_customers,prospect_pdt.conversion_percent,prospect_pdt.total_revenue,prospect_pdt.average_revenue,prospect_pdt.sub_affiliate_breakdown&f[prospect_pdt.date_select]={}&f[prospect_pdt.is_test]=0&f[prospect_pdt.affiliate_id]=&f[prospect_pdt.sub_affiliate_id]=&f[prospect_pdt.currency_symbol]=$&f[prospect_pdt.currency_fmt]=&f[prospect_pdt.campaign]=&f[prospect_pdt.campaign_disp]={}&query_timezone=America/New_York&limit=500&querySource=drill_modal&path_prefix=/embed/explore").format
            response = requests.post(url('+'.join(date.split()), '+'.join(campaign_name.split())), headers=header)
            details = response.json()['data']
            sub_results = []
            for detail in details:
                sub_results.append({
                    'id': detail['prospect_pdt.affiliate_id']['value'],
                    'prospects': detail['prospect_pdt.count_prospects']['value'],
                    'initial_customers': detail['prospect_pdt.count_customers']['value'],
                    'conversion_rate': detail['prospect_pdt.conversion_percent']['value'],
                    'gross_revenue': detail['prospect_pdt.total_revenue']['value'],
                    'average_revenue': detail['prospect_pdt.average_revenue']['value'] if detail['prospect_pdt.average_revenue']['value'] else 0,
                })
            cap_results.append([campaign_id, sub_results])

        return results, cap_results

    def get_prospect_report(self, yesterday):
        headers = {'cookie': self.token}
        response = requests.get(self.prospect_url, headers=headers)
        prospect_page = fromstring(response.text)
        iframe_src = prospect_page.xpath('//iframe/@src')[0]

        response = requests.get(iframe_src, headers=headers)
        cookie = response.headers['set-cookie']
        iframe = fromstring(response.text)
        csrf_token = iframe.xpath('//meta[@name="csrf-token"]/@content')[0]

        headers = {
            'cookie': cookie,
            'X-CSRF-Token': csrf_token,
        }

        # get today result
        today, today_cap = self.get_prospect_report_by_date('today', headers)
        print('PROSPECT - TODAY, ' + str(len(today)))

        # get yesterday result
        yesterday_result = []
        yesterday_cap = []
        if yesterday:
            time.sleep(5)
            yesterday_result, yesterday_cap = self.get_prospect_report_by_date('yesterday', headers)
            print('PROSPECT - YESTERDAY, ' + str(len(yesterday_result)))

        # get wtd result
        time.sleep(5)
        wtd, wtd_cap = self.get_prospect_report_by_date(self.week_to_date, headers)
        print('PROSPECT - WEEK TO DATE, ' + str(len(wtd)))

        return today, yesterday_result, wtd, today_cap, yesterday_cap, wtd_cap

    def get_retention_report_by_date(self, date, header):
        start_ms = str(int(timezone.now().timestamp() * 1000))
        # data = '[{"result_maker_id":31178,"merge_result_id":null,"query_id":3038468,"vis_config":{"show_view_names":false,"show_row_numbers":false,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"series_labels":{"orders_retention.rebill_depth":"Subscription Cycle"},"table_theme":"gray","limit_displayed_rows":false,"enable_conditional_formatting":false,"conditional_formatting":[{"type":"along a scale...","value":null,"background_color":"#3EC9FF","font_color":null,"color_application":{"collection_id":"729db87a-f0f9-45f2-af34-0c293dce8e46","palette_id":"865e83bc-79ce-486b-bcfd-8d491868aa95","options":{"constraints":{"min":{"type":"minimum"},"mid":{"type":"number","value":0},"max":{"type":"maximum"}},"mirror":true,"reverse":false,"stepped":false}},"bold":false,"italic":false,"strikethrough":false,"fields":null}],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false,"pinned_columns":{"orders_retention.campaign":"left"},"transpose":false,"truncate_text":false,"size_to_fit":true,"series_column_widths":{"orders_retention.campaign":178,"orders_retention.transactions":124,"orders_retention.orders":84,"orders_retention.subscriptions":95},"series_cell_visualizations":{"orders_retention.transactions":{"is_active":true}},"header_font_color":"#fffff8","header_background_color":"#0d3380","header_text_alignment":"left","header_font_size":"12","rows_font_size":"11","type":"table","hidden_fields":[],"series_types":{},"column_order":["$$$_row_numbers_$$$","orders_retention.campaign","orders_retention.campaign_id","0_orders_retention.transactions","0_orders_retention.orders","0_orders_retention.subscriptions","0_orders_retention.declines","0_orders_retention.void_full_refund","0_orders_retention.partial_refund","0_orders_retention.void_refund_amount","0_orders_retention.holds","0_orders_retention.cancelations","0_orders_retention.pending_subscriptions","0_orders_retention.net_revenue","0_orders_retention.approval_rate_retention","0_conversion","0_retention","1_orders_retention.transactions","1_orders_retention.orders","1_orders_retention.subscriptions","1_orders_retention.declines","1_orders_retention.void_full_refund","1_orders_retention.partial_refund","1_orders_retention.void_refund_amount","1_orders_retention.holds","1_orders_retention.cancelations","1_orders_retention.pending_subscriptions","1_orders_retention.net_revenue","1_orders_retention.approval_rate_retention","1_conversion","1_retention"]},"dynamic_fields":"[{\\"table_calculation\\":\\"conversion\\",\\"label\\":\\"Conversion\\",\\"expression\\":\\"if(pivot_column() = 1, ${orders_retention.approval_rate_retention} , if(pivot_column() = 2, (${orders_retention.orders}/pivot_offset(${orders_retention.subscriptions}, -1)),(${orders_retention.orders}/pivot_offset(${orders_retention.orders}, -1)) ) )\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"},{\\"table_calculation\\":\\"retention\\",\\"label\\":\\"Retention\\",\\"expression\\":\\"if(${orders_retention.orders} <= pivot_offset(${orders_retention.subscriptions},-1),(${orders_retention.orders}/pivot_index(${orders_retention.subscriptions},1)),0)\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"}]","sorts":["orders_retention.rebill_depth 0","orders_retention.campaign 0"],"total":true,"id":3038468,"fill_fields":null,"filters":{"orders_retention.is_test_cc":"No","orders_retention.deleted":"No","orders_retention.date_select":"' + date + '","orders_retention.rebill_depth":">=0","orders_retention.campaign_id":"","orders_retention.afid":"","orders_retention.currency":"USD","orders_retention.products_id":""},"model":"limelight_transactional_reporting","view":"orders_retention","client_id":"djCpDAEYMBRA5ZP0f8Y1N4","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4243,"elementId":29443,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":3038468,"title":"Retention By Campaign"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}},{"result_maker_id":31177,"merge_result_id":null,"query_id":3038466,"vis_config":{"show_view_names":false,"show_row_numbers":false,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"series_labels":{"orders_retention.rebill_depth":"Subscription Cycle","conversion":"Retention"},"table_theme":"gray","limit_displayed_rows":false,"enable_conditional_formatting":false,"conditional_formatting":[{"type":"along a scale...","value":null,"background_color":"#3EC9FF","font_color":null,"color_application":{"collection_id":"729db87a-f0f9-45f2-af34-0c293dce8e46","palette_id":"865e83bc-79ce-486b-bcfd-8d491868aa95","options":{"constraints":{"min":{"type":"minimum"},"mid":{"type":"number","value":0},"max":{"type":"maximum"}},"mirror":true,"reverse":false,"stepped":false}},"bold":false,"italic":false,"strikethrough":false,"fields":null}],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false,"pinned_columns":{"orders_retention.campaign":"left"},"transpose":false,"truncate_text":false,"size_to_fit":true,"series_column_widths":{"orders_retention.campaign":178,"orders_retention.transactions":124,"orders_retention.orders":84,"orders_retention.subscriptions":95},"series_cell_visualizations":{"orders_retention.transactions":{"is_active":true}},"header_font_color":"#fffff8","header_background_color":"#0d3380","header_text_alignment":"left","header_font_size":"12","rows_font_size":"11","type":"table","hidden_fields":["orders_retention.subscriptions","orders_retention.approval_rate_retention","retention"],"series_types":{},"column_order":["$$$_row_numbers_$$$","orders_retention.campaign","orders_retention.campaign_id","0_orders_retention.transactions","0_orders_retention.orders","0_orders_retention.subscriptions","0_orders_retention.declines","0_orders_retention.void_full_refund","0_orders_retention.partial_refund","0_orders_retention.void_refund_amount","0_orders_retention.holds","0_orders_retention.cancelations","0_orders_retention.pending_subscriptions","0_orders_retention.net_revenue","0_orders_retention.approval_rate_retention","0_conversion","0_retention","1_orders_retention.transactions","1_orders_retention.orders","1_orders_retention.subscriptions","1_orders_retention.declines","1_orders_retention.void_full_refund","1_orders_retention.partial_refund","1_orders_retention.void_refund_amount","1_orders_retention.holds","1_orders_retention.cancelations","1_orders_retention.pending_subscriptions","1_orders_retention.net_revenue","1_orders_retention.approval_rate_retention","1_conversion","1_retention"]},"dynamic_fields":"[{\\"table_calculation\\":\\"conversion\\",\\"label\\":\\"Conversion\\",\\"expression\\":\\"if(pivot_column() = 1, ${orders_retention.approval_rate_retention} , if(pivot_column() = 2, (${orders_retention.orders}/pivot_offset(${orders_retention.subscriptions}, -1)),(${orders_retention.orders}/pivot_offset(${orders_retention.orders}, -1)) ) )\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"},{\\"table_calculation\\":\\"retention\\",\\"label\\":\\"Retention\\",\\"expression\\":\\"if(${orders_retention.orders} <= pivot_offset(${orders_retention.subscriptions},-1),(${orders_retention.orders}/pivot_index(${orders_retention.subscriptions},1)),0)\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"}]","sorts":["orders_retention.rebill_depth 0","orders_retention.campaign 0"],"total":null,"id":3038466,"fill_fields":null,"filters":{"orders_retention.date_select":"' + date + '","orders_retention.rebill_depth":">=0","orders_retention.campaign_id":"","orders_retention.afid":"","orders_retention.currency":"USD","orders_retention.is_test_cc":"No","orders_retention.products_id":""},"model":"limelight_transactional_reporting","view":"orders_retention","client_id":"eTmDesNOcEeSGf6s0s0wWx","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4243,"elementId":29444,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":3038466,"title":"Retention Rate By Campaign"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}},{"result_maker_id":13138,"merge_result_id":null,"query_id":1110138,"vis_config":{"show_view_names":false,"show_row_numbers":true,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"table_theme":"gray","limit_displayed_rows":false,"enable_conditional_formatting":true,"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false,"stacking":"","show_value_labels":false,"label_density":25,"legend_position":"center","x_axis_gridlines":false,"y_axis_gridlines":true,"y_axis_combined":true,"show_y_axis_labels":true,"show_y_axis_ticks":true,"y_axis_tick_density":"default","y_axis_tick_density_custom":5,"show_x_axis_label":true,"show_x_axis_ticks":true,"x_axis_scale":"auto","y_axis_scale_mode":"linear","x_axis_reversed":false,"y_axis_reversed":false,"show_null_points":true,"point_style":"none","interpolation":"linear","show_totals_labels":false,"show_silhouette":false,"totals_color":"#808080","ordering":"none","show_null_labels":false,"type":"table","series_types":{},"x_axis_label":"Month","y_axes":[{"label":"Revenue","maxValue":null,"minValue":null,"orientation":"left","showLabels":true,"showValues":true,"tickDensity":"default","tickDensityCustom":5,"type":"linear","unpinAxis":false,"valueFormat":"$#,###","series":[{"id":"Affiliate","name":"Affiliate","axisId":"f_orders.order_total_approved"},{"id":"ChillderCamp","name":"ChillderCamp","axisId":"f_orders.order_total_approved"},{"id":"Email","name":"Email","axisId":"f_orders.order_total_approved"},{"id":"?","name":"?","axisId":"f_orders.order_total_approved"}]}],"conditional_formatting":[{"type":"low to high","value":null,"background_color":null,"font_color":null,"palette":{"name":"Red to Yellow to Green","colors":["#F36254","#FCF758","#4FBC89"]},"bold":false,"italic":false,"strikethrough":false,"fields":null}]},"dynamic_fields":null,"sorts":["f_orders.acquisition_date_month 0","f_orders.rebill_rate desc 0"],"total":null,"id":1110138,"fill_fields":["f_orders.acquisition_date_month"],"filters":{"f_orders.acquisition_date_date":"6 months ago for 6 months","f_orders.afid":"","f_orders.is_deleted":"No"},"model":"limelightcrm","view":"f_orders","client_id":"9owfOPJ2S1pl4SV8ECeZZc","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4243,"elementId":29442,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":1110138,"title":"Rebill Rate (last 6 complete months)"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}},{"result_maker_id":31179,"merge_result_id":null,"query_id":3038470,"vis_config":{"show_view_names":false,"show_row_numbers":false,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"series_labels":{"orders_retention.rebill_depth":"Subscription Cycle"},"table_theme":"gray","limit_displayed_rows":false,"enable_conditional_formatting":false,"conditional_formatting":[{"type":"along a scale...","value":null,"background_color":"#3EC9FF","font_color":null,"color_application":{"collection_id":"729db87a-f0f9-45f2-af34-0c293dce8e46","palette_id":"865e83bc-79ce-486b-bcfd-8d491868aa95","options":{"constraints":{"min":{"type":"minimum"},"mid":{"type":"number","value":0},"max":{"type":"maximum"}},"mirror":true,"reverse":false,"stepped":false}},"bold":false,"italic":false,"strikethrough":false,"fields":null}],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false,"pinned_columns":{"orders_retention.campaign":"left"},"transpose":false,"truncate_text":false,"size_to_fit":true,"series_column_widths":{"orders_retention.campaign":178,"orders_retention.transactions":124,"orders_retention.orders":84,"orders_retention.subscriptions":95},"series_cell_visualizations":{"orders_retention.transactions":{"is_active":true}},"header_font_color":"#fffff8","header_background_color":"#0d3380","header_text_alignment":"left","header_font_size":"12","rows_font_size":"11","type":"table","hidden_fields":[],"series_types":{},"column_order":["$$$_row_numbers_$$$","orders_retention.campaign","orders_retention.campaign_id","0_orders_retention.transactions","0_orders_retention.orders","0_orders_retention.subscriptions","0_orders_retention.declines","0_orders_retention.void_full_refund","0_orders_retention.partial_refund","0_orders_retention.void_refund_amount","0_orders_retention.holds","0_orders_retention.cancelations","0_orders_retention.pending_subscriptions","0_orders_retention.net_revenue","0_orders_retention.approval_rate_retention","0_conversion","0_retention","1_orders_retention.transactions","1_orders_retention.orders","1_orders_retention.subscriptions","1_orders_retention.declines","1_orders_retention.void_full_refund","1_orders_retention.partial_refund","1_orders_retention.void_refund_amount","1_orders_retention.holds","1_orders_retention.cancelations","1_orders_retention.pending_subscriptions","1_orders_retention.net_revenue","1_orders_retention.approval_rate_retention","1_conversion","1_retention"]},"dynamic_fields":"[{\\"table_calculation\\":\\"conversion\\",\\"label\\":\\"Conversion\\",\\"expression\\":\\"if(pivot_column() = 1, ${orders_retention.approval_rate_retention} , if(pivot_column() = 2, (${orders_retention.orders}/pivot_offset(${orders_retention.subscriptions}, -1)),(${orders_retention.orders}/pivot_offset(${orders_retention.orders}, -1)) ) )\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"},{\\"table_calculation\\":\\"retention\\",\\"label\\":\\"Retention\\",\\"expression\\":\\"if(${orders_retention.orders} <= pivot_offset(${orders_retention.subscriptions},-1),(${orders_retention.orders}/pivot_index(${orders_retention.subscriptions},1)),0)\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"}]","sorts":["orders_retention.rebill_depth 0","orders_retention.transactions desc 0"],"total":true,"id":3038470,"fill_fields":null,"filters":{"orders_retention.select_dimension":"campaign^_id","orders_retention.select_dimension_2":"affiliate^_id","orders_retention.select_dimension_3":"sub^_affiliate^_id","orders_retention.date_select":"' + date + '","orders_retention.rebill_depth":">=0","orders_retention.campaign_id":"","orders_retention.afid":"","orders_retention.currency":"USD","orders_retention.is_test_cc":"No","orders_retention.products_id":""},"model":"limelight_transactional_reporting","view":"orders_retention","client_id":"m1Rjyo7nznYJEoz51VSPnN","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4243,"elementId":29445,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":3038470,"title":"Retention by Selected Dimension"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}}]'
        data = '[{"result_maker_id":31178,"merge_result_id":null,"query_id":3038468,"vis_config":{"show_view_names":false,"show_row_numbers":false,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"series_labels":{"orders_retention.rebill_depth":"Subscription Cycle"},"table_theme":"gray","limit_displayed_rows":false,"enable_conditional_formatting":false,"conditional_formatting":[{"type":"along a scale...","value":null,"background_color":"#3EC9FF","font_color":null,"color_application":{"collection_id":"729db87a-f0f9-45f2-af34-0c293dce8e46","palette_id":"865e83bc-79ce-486b-bcfd-8d491868aa95","options":{"constraints":{"min":{"type":"minimum"},"mid":{"type":"number","value":0},"max":{"type":"maximum"}},"mirror":true,"reverse":false,"stepped":false}},"bold":false,"italic":false,"strikethrough":false,"fields":null}],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false,"pinned_columns":{"orders_retention.campaign":"left"},"transpose":false,"truncate_text":false,"size_to_fit":true,"series_column_widths":{"orders_retention.campaign":178,"orders_retention.transactions":124,"orders_retention.orders":84,"orders_retention.subscriptions":95},"series_cell_visualizations":{"orders_retention.transactions":{"is_active":true}},"header_font_color":"#fffff8","header_background_color":"#0d3380","header_text_alignment":"left","header_font_size":"12","rows_font_size":"11","type":"table","hidden_fields":[],"series_types":{},"column_order":["$$$_row_numbers_$$$","orders_retention.campaign","orders_retention.campaign_id","0_orders_retention.transactions","0_orders_retention.orders","0_orders_retention.subscriptions","0_orders_retention.declines","0_orders_retention.void_full_refund","0_orders_retention.partial_refund","0_orders_retention.void_refund_amount","0_orders_retention.holds","0_orders_retention.cancelations","0_orders_retention.pending_subscriptions","0_orders_retention.net_revenue","0_orders_retention.approval_rate_retention","0_conversion","0_retention","1_orders_retention.transactions","1_orders_retention.orders","1_orders_retention.subscriptions","1_orders_retention.declines","1_orders_retention.void_full_refund","1_orders_retention.partial_refund","1_orders_retention.void_refund_amount","1_orders_retention.holds","1_orders_retention.cancelations","1_orders_retention.pending_subscriptions","1_orders_retention.net_revenue","1_orders_retention.approval_rate_retention","1_conversion","1_retention"]},"dynamic_fields":"[{\\"table_calculation\\":\\"conversion\\",\\"label\\":\\"Conversion\\",\\"expression\\":\\"if(pivot_column() = 1, ${orders_retention.approval_rate_retention} , if(pivot_column() = 2, (${orders_retention.orders}/pivot_offset(${orders_retention.subscriptions}, -1)),(${orders_retention.orders}/pivot_offset(${orders_retention.orders}, -1)) ) )\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"},{\\"table_calculation\\":\\"retention\\",\\"label\\":\\"Retention\\",\\"expression\\":\\"if(${orders_retention.orders} <= pivot_offset(${orders_retention.subscriptions},-1),(${orders_retention.orders}/pivot_index(${orders_retention.subscriptions},1)),0)\\",\\"value_format\\":null,\\"value_format_name\\":\\"percent_2\\",\\"_kind_hint\\":\\"measure\\",\\"_type_hint\\":\\"number\\"}]","sorts":["orders_retention.rebill_depth 0","orders_retention.campaign 0"],"total":true,"id":3038468,"fill_fields":null,"filters":{"orders_retention.is_test_cc":"No","orders_retention.deleted":"No","orders_retention.date_select":"' + date + '","orders_retention.rebill_depth":">=0","orders_retention.campaign_id":"","orders_retention.afid":"","orders_retention.currency":"USD","orders_retention.products_id":""},"model":"limelight_transactional_reporting","view":"orders_retention","client_id":"djCpDAEYMBRA5ZP0f8Y1N4","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4243,"elementId":29443,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":3038468,"title":"Retention By Campaign"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}}]'
        response = requests.post(self.subdomain + '.analytics.limelightcrm.com/api/internal/queries/multi_run_async', data=data, headers=header)
        task_id = response.json()[0]['query_task_id']

        requests.post(self.subdomain + '.analytics.limelightcrm.com/api/internal/queries/async_long_poll', data='["' + task_id + '"]', headers=header)

        url = (self.subdomain + ".analytics.limelightcrm.com/api/internal/query_tasks/multi_results?query_task_ids[]={}").format
        response = requests.get(url(task_id), headers=header)
        result = response.json()

        retentions = result[task_id]['data']['data']
        results = []
        for retention in retentions:
            campaign = retention['orders_retention.campaign']['value']
            campaign_id = campaign.split(')')[0][1:]
            data = {
                'campaign_id': int(campaign_id),  # Campaign
                'campaign_name': campaign.replace('(' + campaign_id + ') ', ''),  # Campaign
                'gross_orders': retention['orders_retention.orders']['0']['value'],  # Orders
                'net_approved': retention['orders_retention.transactions']['0']['value'],  # Transactions
                'subscriptions_approved': retention['orders_retention.subscriptions']['0']['value'],  # Subscriptions
                'declined': retention['orders_retention.declines']['0']['value'],  # Declines
                'void_full_refund': retention['orders_retention.void_full_refund']['0']['value'],  # Void Full Refund
                'partial_refund': retention['orders_retention.partial_refund']['0']['value'],  # Partial Refund
                'void_refund_revenue': retention['orders_retention.void_refund_amount']['0']['value'],  # Void Refund Amount
                'canceled': retention['orders_retention.cancelations']['0']['value'],  # Cancelations
                'hold': retention['orders_retention.holds']['0']['value'],  # Holds
                'pending': retention['orders_retention.pending_subscriptions']['0']['value'],  # Pending Subscriptions
                'approval_rate': retention['orders_retention.approval_rate_retention']['0']['value'],  # Billing Rate
                'net_revenue': retention['orders_retention.net_revenue']['0']['value'],  # Net Revenue
            }
            results.append(data)
        return results

    def get_retention_report(self, yesterday):
        headers = {'cookie': self.token}
        response = requests.get(self.retention_url, headers=headers)
        prospect_page = fromstring(response.text)
        iframe_src = prospect_page.xpath('//iframe/@src')[0]

        response = requests.get(iframe_src, headers=headers)
        cookie = response.headers['set-cookie']
        iframe = fromstring(response.text)
        csrf_token = iframe.xpath('//meta[@name="csrf-token"]/@content')[0]

        headers = {
            'cookie': cookie,
            'X-CSRF-Token': csrf_token,
        }

        # get today result
        today = self.get_retention_report_by_date('today', headers)
        print('RETENTION - TODAY, ' + str(len(today)))

        # get yesterday result
        yesterday_result = []
        if yesterday:
            time.sleep(5)
            yesterday_result = self.get_retention_report_by_date('yesterday', headers)
            print('RETENTION - YESTERDAY, ' + str(len(yesterday_result)))

        # get wtd result
        time.sleep(5)
        wtd = self.get_retention_report_by_date(self.week_to_date, headers)
        print('RETENTION - WEEK TO DATE, ' + str(len(wtd)))

        return today, yesterday_result, wtd
