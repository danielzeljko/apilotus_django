import psycopg2

conn = psycopg2.connect(
    host="pro.apilotus.com",
    database="apilotus",
    user="apilotus",
    password="1g2cp0uk",
)
cursor = conn.cursor()

dash_campaigns = '''
165	,1,5,8,
166	,1,6,8,
167	,3,1,8,
168	,4,1,8,
169	,2,5,8,
170	,2,6,8,
171	,3,2,8,
172	,4,2,8,
'''
dash_campaigns = [a.split('\t') for a in dash_campaigns.split('\n')[1:-1]]
ok = True

crm_id = 15
query = "SELECT * FROM lotus_dashboard_labelcampaign WHERE crm_id=" + str(crm_id) + " ORDER BY campaign_id"
cursor.execute(query)
pro_campaigns = cursor.fetchall()

count = 0
campaign_types = []
campaign_formats = []
label_ids = []

dash_ids = []
pro_ids = []

for campaign in dash_campaigns:
    dash_ids.append(int(campaign[0]))

for item in pro_campaigns:
    for campaign in dash_campaigns:
        if int(campaign[0]) == item[1]:
            pro_ids.append(item[1])
            count += 1

            a = campaign[1][1:-1].split(',')
            if len(a) == 2:
                campaign_type = int(a[0])
                label_id = int(a[1])
                print(campaign[0], campaign_type, label_id)
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

                if ok:
                    query = "UPDATE lotus_dashboard_labelcampaign SET campaign_type = {}, label_id = {} WHERE crm_id = {} AND campaign_id = {}".format
                    cursor.execute(query(campaign_type, label_id, crm_id, item[1]))
            elif len(a) == 3:
                campaign_type = int(a[0])
                campaign_format = int(a[1])
                label_id = int(a[2])
                print(campaign[0], campaign_type, campaign_format, label_id)
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

                if ok:
                    query = "UPDATE lotus_dashboard_labelcampaign SET campaign_type = {}, campaign_format = {}, label_id = {} WHERE crm_id = {} AND campaign_id = {}".format
                    cursor.execute(query(campaign_type, campaign_format, label_id, crm_id, item[1]))
            else:
                print('-------------')

print(set(campaign_types), set(campaign_formats), set(label_ids))
print(set(dash_ids) - set(pro_ids))
print(len(dash_ids), count)

conn.commit()
cursor.close()
conn.close()
