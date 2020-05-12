import requests
from lxml.html import fromstring
from datetime import datetime

# Login
data = {
    'admin_name': 'api-tool',
    'admin_pass': 'h8*)e5ug03Q4',
}
response = requests.post('https://buyid.limelightcrm.com/admin/login.php', data=data)
token = response.headers['set-cookie'].split(';')[0]
print(token)

# Redirect to Prospect page
headers = {'cookie': token}
response = requests.get('https://buyid.limelightcrm.com/admin/reports/index.php?d=Sales+By+Prospects', headers=headers)
prospect_page = fromstring(response.text)
iframe_src = prospect_page.xpath('//iframe/@src')[0]
print(iframe_src)

# Redirect to iframe Link
response = requests.get(iframe_src, headers=headers)
new_token = response.headers['set-cookie']
print(new_token)
iframe = fromstring(response.text)
csrf_token = iframe.xpath('//meta[@name="csrf-token"]/@content')[0]
print(csrf_token)

new_header = {
    'cookie': new_token,
    'X-CSRF-Token': csrf_token,
}

date = 'today'
# yesterday
# 2019/11/25 to 2019/11/27
start_ms = str(int(datetime.now().timestamp() * 1000))
data = '[{"result_maker_id":12842,"merge_result_id":null,"query_id":1083454,"vis_config":{"show_view_names":true,"show_row_numbers":true,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"table_theme":"gray","limit_displayed_rows":false,"type":"table","stacking":"","show_value_labels":false,"label_density":25,"legend_position":"center","x_axis_gridlines":false,"y_axis_gridlines":true,"y_axis_combined":true,"show_y_axis_labels":true,"show_y_axis_ticks":true,"y_axis_tick_density":"default","y_axis_tick_density_custom":5,"show_x_axis_label":true,"show_x_axis_ticks":true,"x_axis_scale":"auto","y_axis_scale_mode":"linear","ordering":"none","show_null_labels":false,"show_totals_labels":false,"show_silhouette":false,"totals_color":"#808080","series_types":{},"series_labels":{"prospect_pdt.campaign_disp":"Campaign","prospect_pdt.count_prospects":"Prospects","prospect_pdt.count_customers":"Initial Customers","prospect_pdt.conversion_percent":"Conversion Rate","prospect_pdt.total_revenue":"Gross Revenue","prospect_pdt.average_revenue":"AOV","prospect_pdt.affiliate_breakdown":"Affiliate Breakdown"},"enable_conditional_formatting":false,"conditional_formatting_ignored_fields":[],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false},"dynamic_fields":null,"sorts":["prospect_pdt.count_prospects desc"],"total":true,"id":1083454,"fill_fields":null,"filters":{"prospect_pdt.date_select":"' + date + '","prospect_pdt.is_test":"0","prospect_pdt.currency_fmt":"","prospect_pdt.campaign":"","prospect_pdt.campaign_disp":"","prospect_pdt.product_id":"","prospect_pdt.affiliate_id":"","prospect_pdt.sub_affiliate_id":""},"model":"limelight_transactional_reporting","view":"prospect_pdt","client_id":"ZRLmeEziCfjgPfEvGv7W6r","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4088,"elementId":28074,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":1083454,"title":"Sales By Prospects"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}}]'
response = requests.post(
    'https://buyid.analytics.limelightcrm.com/api/internal/queries/multi_run_async',
    data=data,
    headers=new_header,
)
task_id_1 = response.json()[0]['query_task_id']
# task_id_2 = response.json()[1]['query_task_id']

url = "https://buyid.analytics.limelightcrm.com/api/internal/query_tasks/multi_results?query_task_ids[]={}".format
response = requests.get(url(task_id_1), headers=new_header)
result = response.json()

status = result[task_id_1]['status']
if status == 'complete':
    prospects = result[task_id_1]['data']['data']
    for prospect in prospects:
        print(prospect)
        campaign_name = prospect['prospect_pdt.campaign_disp']['value']
        url = "https://buyid.analytics.limelightcrm.com/api/internal/models/limelight_transactional_reporting/views/prospect_pdt?fields=prospect_pdt.affiliate_id,prospect_pdt.count_prospects,prospect_pdt.count_customers,prospect_pdt.conversion_percent,prospect_pdt.total_revenue,prospect_pdt.average_revenue,prospect_pdt.sub_affiliate_breakdown&f[prospect_pdt.date_select]={}&f[prospect_pdt.is_test]=0&f[prospect_pdt.affiliate_id]=&f[prospect_pdt.sub_affiliate_id]=&f[prospect_pdt.currency_symbol]=$&f[prospect_pdt.currency_fmt]=&f[prospect_pdt.campaign]=&f[prospect_pdt.campaign_disp]={}&query_timezone=America/New_York&limit=500&querySource=drill_modal&path_prefix=/embed/explore".format
        response = requests.post(url(date, '+'.join(campaign_name.split())), headers=new_header)
        sub_afids = response.json()['data']
        for detail in sub_afids:
            data = {
                'id': detail['prospect_pdt.affiliate_id']['value'],
                'prospects': detail['prospect_pdt.count_prospects']['value'],
                'initial_customers': detail['prospect_pdt.count_customers']['value'],
                'conversion_rate': detail['prospect_pdt.conversion_percent']['value'],
                'gross_revenue': detail['prospect_pdt.total_revenue']['value'],
                'average_revenue': detail['prospect_pdt.average_revenue']['value'],
            }
            print(data)


# print('----------------------------------')
# date = 'today'
# date = 'yesterday'
# date = '2020/01/01 to 2020/04/12'
# start_ms = str(int(datetime.now().timestamp() * 1000))
# data = '[{"result_maker_id":12842,"merge_result_id":null,"query_id":1083454,"vis_config":{"show_view_names":true,"show_row_numbers":true,"truncate_column_names":false,"hide_totals":false,"hide_row_totals":false,"table_theme":"gray","limit_displayed_rows":false,"type":"table","stacking":"","show_value_labels":false,"label_density":25,"legend_position":"center","x_axis_gridlines":false,"y_axis_gridlines":true,"y_axis_combined":true,"show_y_axis_labels":true,"show_y_axis_ticks":true,"y_axis_tick_density":"default","y_axis_tick_density_custom":5,"show_x_axis_label":true,"show_x_axis_ticks":true,"x_axis_scale":"auto","y_axis_scale_mode":"linear","ordering":"none","show_null_labels":false,"show_totals_labels":false,"show_silhouette":false,"totals_color":"#808080","series_types":{},"series_labels":{"prospect_pdt.campaign_disp":"Campaign","prospect_pdt.count_prospects":"Prospects","prospect_pdt.count_customers":"Initial Customers","prospect_pdt.conversion_percent":"Conversion Rate","prospect_pdt.total_revenue":"Gross Revenue","prospect_pdt.average_revenue":"AOV","prospect_pdt.affiliate_breakdown":"Affiliate Breakdown"},"enable_conditional_formatting":false,"conditional_formatting_ignored_fields":[],"conditional_formatting_include_totals":false,"conditional_formatting_include_nulls":false},"dynamic_fields":null,"sorts":["prospect_pdt.count_prospects desc"],"total":true,"id":1083454,"fill_fields":null,"filters":{"prospect_pdt.date_select":"' + date + '","prospect_pdt.is_test":"0","prospect_pdt.currency_fmt":"","prospect_pdt.campaign":"","prospect_pdt.campaign_disp":"","prospect_pdt.affiliate_id":"","prospect_pdt.sub_affiliate_id":""},"model":"limelight_transactional_reporting","view":"prospect_pdt","client_id":"ZRLmeEziCfjgPfEvGv7W6r","query_timezone":"America/New_York","row_total":null,"source":"dashboard","path_prefix":"/embed/explore","generate_links":true,"force_production":true,"server_table_calcs":false,"cache":true,"cache_only":true,"dashboard_id":4088,"elementId":28074,"parentSpan":{"_startMs":' + start_ms + ',"_finishMs":0,"_operationName":"DASHBOARD_ELEMENT","_tags":{"id":1083454,"title":"Sales By Prospects"},"_baggage":{},"_references":[{"_type":"child_of"}],"_timer":{}}}]'
# response = requests.post(
#     'https://buyid.analytics.limelightcrm.com/api/internal/queries/multi_run_async',
#     data=data,
#     headers=new_header,
# )
# task_id_1 = response.json()[0]['query_task_id']
#
# while True:
#     response = requests.post('https://buyid.analytics.limelightcrm.com/api/internal/queries/async_long_poll',
#                              data='["' + task_id_1 + '"]',
#                              headers=new_header,
#                              )
#     print(response.json())
#
#     url = "https://buyid.analytics.limelightcrm.com/api/internal/query_tasks/multi_results?query_task_ids[]={}".format
#     response = requests.get(url(task_id_1), headers=new_header)
#     result = response.json()
#     if result[task_id_1]['status'] == 'complete':
#         break
#
# prospects = result[task_id_1]['data']['data']
# for prospect in prospects:
#     print(prospect)
