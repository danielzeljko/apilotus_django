import psycopg2
import pymysql

crm_match = {
    59: 1,
    75: 2,
    83: 3,
    84: 4,
    89: 5,
    93: 6,
    94: 7,
    95: 8,
    98: 9,
    100: 10,
    101: 11,
    102: 12,
    103: 13,
    104: 14,
    105: 15,
}

dash_conn = pymysql.connect(
    host="dash.apilotus.com",
    database="commercials_apilotus",
    user="root",
    password="apilotusdb123456",
)
dash_cursor = dash_conn.cursor()

pro_conn = psycopg2.connect(
    host="pro.apilotus.com",
    database="apilotus",
    user="apilotus",
    password="1g2cp0uk",
)
pro_cursor = pro_conn.cursor()

query = "SELECT * FROM primary_crm_account"
dash_cursor.execute(query)
dash_crms = dash_cursor.fetchall()

for dash_crm in dash_crms:
    print(dash_crm)
    query = "SELECT * FROM primary_label_campaign WHERE crm_id=" + str(dash_crm[0])
    dash_cursor.execute(query)
    dash_campaigns = dash_cursor.fetchall()

    crm_id = crm_match[dash_crm[0]]
    query = "SELECT * FROM lotus_dashboard_labelcampaign WHERE crm_id=" + str(crm_id) + " ORDER BY campaign_id"
    pro_cursor.execute(query)
    pro_campaigns = pro_cursor.fetchall()

    count = 0
    campaign_types = []
    campaign_formats = []
    label_ids = []

    dash_ids = []
    pro_ids = []

    for campaign in dash_campaigns:
        dash_ids.append(campaign[2])

    for item in pro_campaigns:
        for campaign in dash_campaigns:
            if campaign[2] == item[1]:
                pro_ids.append(item[1])
                count += 1

                a = campaign[3][1:-1].split(',')
                if len(a) == 2:
                    campaign_type = int(a[0])
                    label_id = int(a[1])
                    campaign_types.append(campaign_type)
                    label_ids.append(label_id)

                    if label_id == 7:
                        label_id = 1
                    elif label_id == 8:
                        label_id = 2
                    elif label_id == 9:
                        label_id = 3
                    elif label_id == 12:
                        label_id = 4
                    elif label_id == 14:
                        label_id = 5
                    elif label_id == 31:
                        label_id = 6

                    if item[3] == campaign_type and item[6] == label_id:
                        pass
                    else:
                        query = "UPDATE lotus_dashboard_labelcampaign SET campaign_type = {}, label_id = {} WHERE crm_id = {} AND campaign_id = {}".format
                        pro_cursor.execute(query(campaign_type, label_id, crm_id, item[1]))
                        print(campaign[2], campaign_type, label_id)
                elif len(a) == 3:
                    campaign_type = int(a[0])
                    campaign_format = int(a[1])
                    label_id = int(a[2])
                    campaign_types.append(campaign_type)
                    campaign_formats.append(campaign_format)
                    label_ids.append(label_id)

                    if label_id == 7:
                        label_id = 1
                    elif label_id == 8:
                        label_id = 2
                    elif label_id == 9:
                        label_id = 3
                    elif label_id == 12:
                        label_id = 4
                    elif label_id == 14:
                        label_id = 5
                    elif label_id == 31:
                        label_id = 6

                    if campaign_format == 5:
                        campaign_format = 3
                    elif campaign_format == 6:
                        campaign_format = 4

                    if item[3] == campaign_type and item[4] == campaign_format and item[6] == label_id:
                        pass
                    else:
                        query = "UPDATE lotus_dashboard_labelcampaign SET campaign_type = {}, campaign_format = {}, label_id = {} WHERE crm_id = {} AND campaign_id = {}".format
                        pro_cursor.execute(query(campaign_type, campaign_format, label_id, crm_id, item[1]))
                        print(campaign[2], campaign_type, campaign_format, label_id)
                else:
                    print('-------------')

    # print(set(campaign_types), set(campaign_formats), set(label_ids))
    # print(set(dash_ids) - set(pro_ids))
    # print(len(dash_ids), count)

dash_cursor.close()
dash_conn.close()

pro_conn.commit()
pro_cursor.close()
pro_conn.close()
