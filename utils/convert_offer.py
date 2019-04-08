import psycopg2
import pymysql

conn = psycopg2.connect(
    host="pro.apilotus.com",
    database="apilotus",
    user="apilotus",
    password="1g2cp0uk",
)
cursor = conn.cursor()

mysql_conn = pymysql.connect(
    user="root", password="apilotusdb123456",
    host="localhost", database="commercials_apilotus")
mysql_cursor = mysql_conn.cursor()

query = "SELECT * FROM primary_crm_account WHERE paused=0"
mysql_cursor.execute(query)
crms = mysql_cursor.fetchall()

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
for crm in crms:
    query = "SELECT * FROM primary_offer WHERE crm_id=" + str(crm[0])
    mysql_cursor.execute(query)
    offers = mysql_cursor.fetchall()
    print(crm)
    print(offers)

    for offer in offers:
        crm_id = crm_match[offer[2]]

        query = "INSERT INTO lotus_dashboard_offer(name, type, s1_payout, s2_payout, crm_id, label_id) VALUES ('{}', {}, {}, {}, {}, {})".format
        cursor.execute(query(offer[1], offer[5], offer[6], offer[7], crm_id, int(offer[4])))
        cursor.execute('SELECT LASTVAL()')
        offer_id = cursor.fetchone()[0]
        print('inserted offer id -', offer_id)

        offer_strings = offer[3].split(',')
        print(offer_strings)
        for offer_string in offer_strings:
            print(offer_string)
            initial = offer_string.split('_')[0]
            campaign_id = int(offer_string.split('_')[1])
            print(campaign_id)
            query = "SELECT id FROM lotus_dashboard_labelcampaign WHERE crm_id=" + str(crm_id) + " AND campaign_id=" + str(campaign_id)
            cursor.execute(query)
            campaign_id = cursor.fetchone()
            if campaign_id is None:
                print('not exist')
                continue
            campaign_id = campaign_id[0]

            if initial == 'step1':
                query = "INSERT INTO lotus_dashboard_offer_step1(offer_id, labelcampaign_id) VALUES ({}, {})".format
                cursor.execute(query(offer_id, campaign_id))
            elif initial == 'step2':
                query = "INSERT INTO lotus_dashboard_offer_step2(offer_id, labelcampaign_id) VALUES ({}, {})".format
                cursor.execute(query(offer_id, campaign_id))
            elif initial == 'step1pp':
                query = "INSERT INTO lotus_dashboard_offer_step1_prepaids(offer_id, labelcampaign_id) VALUES ({}, {})".format
                cursor.execute(query(offer_id, campaign_id))
            elif initial == 'step2pp':
                query = "INSERT INTO lotus_dashboard_offer_step2_prepaids(offer_id, labelcampaign_id) VALUES ({}, {})".format
                cursor.execute(query(offer_id, campaign_id))
            elif initial == 'step1tab':
                query = "INSERT INTO lotus_dashboard_offer_step1_tablet(offer_id, labelcampaign_id) VALUES ({}, {})".format
                cursor.execute(query(offer_id, campaign_id))
            elif initial == 'step2tab':
                query = "INSERT INTO lotus_dashboard_offer_step2_tablet(offer_id, labelcampaign_id) VALUES ({}, {})".format
                cursor.execute(query(offer_id, campaign_id))

    print('-----------------')

mysql_cursor.close()
mysql_conn.close()

conn.commit()
cursor.close()
conn.close()
