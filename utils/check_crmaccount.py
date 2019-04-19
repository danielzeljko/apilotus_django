import psycopg2
import pymysql

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

query = "SELECT * FROM primary_crm_account"
dash_cursor.execute(query)
dash_crms = dash_cursor.fetchall()

query = "SELECT * FROM lotus_dashboard_crmaccount"
pro_cursor.execute(query)
pro_crms = pro_cursor.fetchall()

for dash_crm in dash_crms:
    for pro_crm in pro_crms:
        if crm_match[dash_crm[0]] == pro_crm[0]:
            print(dash_crm[1:])
            print(pro_crm[1:])
            if dash_crm[7] != pro_crm[7] or bool(dash_crm[8]) != pro_crm[8]:
                print('---------')

dash_cursor.close()
dash_conn.close()

pro_conn.commit()
pro_cursor.close()
pro_conn.close()
