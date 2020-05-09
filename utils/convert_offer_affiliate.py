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

query = "SELECT * FROM primary_affiliate"
dash_cursor.execute(query)
dash_affiliates = dash_cursor.fetchall()

for affiliate in dash_affiliates:
    query = "SELECT * FROM lotus_dashboard_affiliate WHERE name='{}'".format
    pro_cursor.execute(query(affiliate[1]))
    if pro_cursor.rowcount > 0:
        pro_affiliate = pro_cursor.fetchone()
        if pro_affiliate[2] != affiliate[2]:
            print('afid different', pro_affiliate)
    else:
        query = "INSERT INTO lotus_dashboard_affiliate(name, afid) VALUES ('{}', '{}')".format
        pro_cursor.execute(query(affiliate[1], affiliate[2]))
        print('inserted affiliate -', affiliate[1], affiliate[2], affiliate[3], affiliate[4])


query = "SELECT * FROM primary_affiliate_goal"
dash_cursor.execute(query)
dash_affiliate_offers = dash_cursor.fetchall()

pro_cursor.execute('DELETE FROM lotus_dashboard_affiliateoffer')
pro_cursor.execute('ALTER SEQUENCE lotus_dashboard_affiliateoffer_id_seq RESTART WITH 1;')

for dash_affiliate in dash_affiliates:
    for dash_affiliate_offer in dash_affiliate_offers:
        if dash_affiliate[0] == dash_affiliate_offer[1]:
            query = "SELECT * FROM lotus_dashboard_affiliate WHERE name='" + dash_affiliate[1] + "'"
            pro_cursor.execute(query)
            pro_affiliate = pro_cursor.fetchone()
            pro_affiliate_id = pro_affiliate[0]

            query = "SELECT * FROM primary_offer WHERE id=" + str(dash_affiliate_offer[2])
            dash_cursor.execute(query)
            dash_offer = dash_cursor.fetchone()

            query = "SELECT * FROM lotus_dashboard_offer WHERE name='{}' AND crm_id={}".format
            pro_cursor.execute(query(dash_offer[1].replace("'", "''"), crm_match[dash_offer[2]]))
            pro_offer = pro_cursor.fetchone()
            pro_offer_id = pro_offer[0]

            query = "INSERT INTO lotus_dashboard_affiliateoffer(goal, s1_payout, s2_payout, affiliate_id, offer_id) VALUES ({}, {}, {}, {}, {})".format
            pro_cursor.execute(query(dash_affiliate_offer[3], dash_affiliate_offer[4], dash_affiliate_offer[5], pro_affiliate_id, pro_offer_id))
            print(pro_affiliate_id, pro_offer_id)


dash_cursor.close()
dash_conn.close()

pro_conn.commit()
pro_cursor.close()
pro_conn.close()
