import psycopg2
import time
from decouple import config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

import requests
from requests.auth import HTTPBasicAuth
import json


pro_conn = psycopg2.connect(
    host=config('DB_HOST'),
    database=config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASSWORD'),
)
pro_cursor = pro_conn.cursor()

query = "SELECT * FROM lotus_dashboard_crmaccount WHERE paused=FALSE ORDER BY id"
pro_cursor.execute(query)
pro_crms = pro_cursor.fetchall()


while True:
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        break
    except Exception as e:
        time.sleep(1)

for crm in pro_crms:
    print(crm)
    driver.get(crm[2] + '/admin')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@name="admin_name"]'))).send_keys(crm[3])
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@name="admin_pass"]'))).send_keys(crm[4])
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//button[@class="btn btn-danger login-page__submit-btn js-sign-in-box-submit-btn"]'))).click()
    time.sleep(2)
driver.close()


class LLCRMAPI(object):
    def __init__(self, url, username, password):
        self.base_url = url + '/api/v1/'
        self.username = username
        self.password = password

    def api_response(self, endpoint):
        response = requests.request("POST", self.base_url + endpoint, auth=HTTPBasicAuth(self.username, self.password))
        return json.loads(response.text)

    def campaigns(self):
        result = self.api_response('campaign_find_active')
        return result


for crm in pro_crms:
    print(crm)
    llcrm_api = LLCRMAPI(crm[2], crm[5], crm[6])
    campaigns = llcrm_api.campaigns()
    if campaigns['response_code'] != '100':
        print(', '.join([crm[1], crm[2], crm[5], crm[6]]))

pro_cursor.close()
pro_conn.close()
