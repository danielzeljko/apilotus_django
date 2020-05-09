import psycopg2
import pymysql
from decouple import config

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
    host=config('DB_HOST'),
    database=config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASSWORD'),
)
pro_cursor = pro_conn.cursor()

query = "SELECT * FROM primary_crm_account"
dash_cursor.execute(query)
dash_crms = dash_cursor.fetchall()

for crm in dash_crms:
    query = "SELECT * FROM primary_offer WHERE crm_id=" + str(crm[0])
    dash_cursor.execute(query)
    offers = dash_cursor.fetchall()
    print(crm)

    for offer in offers:
        print(offer)
        crm_id = crm_match[offer[2]]

        query = "SELECT * FROM lotus_dashboard_offer WHERE name='{}' AND crm_id={}".format
        pro_cursor.execute(query(offer[1].replace("'", "''"), crm_id))
        count = pro_cursor.rowcount

        if count == 0:
            query = "INSERT INTO lotus_dashboard_offer(name, type, s1_payout, s2_payout, crm_id, label_id) VALUES ('{}', {}, {}, {}, {}, {})".format
            pro_cursor.execute(query(offer[1].replace("'", "''"), offer[5], offer[6], offer[7], crm_id, int(offer[4])))
            pro_cursor.execute('SELECT LASTVAL()')
            offer_id = pro_cursor.fetchone()[0]
            print('inserted offer id -', offer_id)
        else:
            offer_id = pro_cursor.fetchone()[0]

        offer_strings = offer[3].split(',')
        # print(offer_strings)
        for offer_string in offer_strings:
            initial = offer_string.split('_')[0]
            campaign_id = int(offer_string.split('_')[1])
            query = "SELECT id FROM lotus_dashboard_labelcampaign WHERE crm_id=" + str(crm_id) + " AND campaign_id=" + str(campaign_id)
            pro_cursor.execute(query)
            campaign_id = pro_cursor.fetchone()
            if campaign_id is None:
                print('not exist', initial, campaign_id)
                continue
            campaign_id = campaign_id[0]

            if initial == 'step1':
                query = "SELECT * FROM lotus_dashboard_offer_step1 WHERE offer_id='{}' AND labelcampaign_id={}".format
                pro_cursor.execute(query(offer_id, campaign_id))
                if pro_cursor.rowcount == 0:
                    query = "INSERT INTO lotus_dashboard_offer_step1(offer_id, labelcampaign_id) VALUES ({}, {})".format
                    pro_cursor.execute(query(offer_id, campaign_id))
                    print(initial, offer_id, campaign_id)
            elif initial == 'step2':
                query = "SELECT * FROM lotus_dashboard_offer_step2 WHERE offer_id='{}' AND labelcampaign_id={}".format
                pro_cursor.execute(query(offer_id, campaign_id))
                if pro_cursor.rowcount == 0:
                    query = "INSERT INTO lotus_dashboard_offer_step2(offer_id, labelcampaign_id) VALUES ({}, {})".format
                    pro_cursor.execute(query(offer_id, campaign_id))
                    print(initial, offer_id, campaign_id)
            elif initial == 'step1pp':
                query = "SELECT * FROM lotus_dashboard_offer_step1_prepaids WHERE offer_id='{}' AND labelcampaign_id={}".format
                pro_cursor.execute(query(offer_id, campaign_id))
                if pro_cursor.rowcount == 0:
                    query = "INSERT INTO lotus_dashboard_offer_step1_prepaids(offer_id, labelcampaign_id) VALUES ({}, {})".format
                    pro_cursor.execute(query(offer_id, campaign_id))
                    print(initial, offer_id, campaign_id)
            elif initial == 'step2pp':
                query = "SELECT * FROM lotus_dashboard_offer_step2_prepaids WHERE offer_id='{}' AND labelcampaign_id={}".format
                pro_cursor.execute(query(offer_id, campaign_id))
                if pro_cursor.rowcount == 0:
                    query = "INSERT INTO lotus_dashboard_offer_step2_prepaids(offer_id, labelcampaign_id) VALUES ({}, {})".format
                    pro_cursor.execute(query(offer_id, campaign_id))
                    print(initial, offer_id, campaign_id)
            elif initial == 'step1tab':
                query = "SELECT * FROM lotus_dashboard_offer_step1_tablet WHERE offer_id='{}' AND labelcampaign_id={}".format
                pro_cursor.execute(query(offer_id, campaign_id))
                if pro_cursor.rowcount == 0:
                    query = "INSERT INTO lotus_dashboard_offer_step1_tablet(offer_id, labelcampaign_id) VALUES ({}, {})".format
                    pro_cursor.execute(query(offer_id, campaign_id))
                    print(initial, offer_id, campaign_id)
            elif initial == 'step2tab':
                query = "SELECT * FROM lotus_dashboard_offer_step2_tablet WHERE offer_id='{}' AND labelcampaign_id={}".format
                pro_cursor.execute(query(offer_id, campaign_id))
                if pro_cursor.rowcount == 0:
                    query = "INSERT INTO lotus_dashboard_offer_step2_tablet(offer_id, labelcampaign_id) VALUES ({}, {})".format
                    pro_cursor.execute(query(offer_id, campaign_id))
                    print(initial, offer_id, campaign_id)

dash_cursor.close()
dash_conn.close()

pro_conn.commit()
pro_cursor.close()
pro_conn.close()
