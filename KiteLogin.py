import requests, json, pyotp
from kiteconnect import KiteConnect
from logging.config import dictConfig
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os

from kiteconnect import KiteTicker
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import re
from Constants import Constants
# from keys import *

def init_logging():
    """
    Initialize the logging framework with the configuration
    :return: Nothing
    :rtype: None
    """
    log_fp = os.path.join(Constants.CONFIG_PATH, Constants.LOG_FILE_NAME)
    print (log_fp)
    if not os.path.exists(log_fp):
        raise FileNotFoundError("Logging configuration file not found!")

    with open(log_fp, mode="r") as log_config:
        dictConfig(config=json.load(log_config))

    # LOGGER.info("Logging framework initialized!")
    print ("Logging framework initialized!")


def load_kite_config():
    """
    Load the kite configuration information from the json file
    :return: A python dictionary
    :rtype: dict
    """
    connect_fp = os.path.join(Constants.CONFIG_PATH, Constants.CONNECTION_INFO_FILE_NAME)

    if not os.path.exists(connect_fp):
        raise FileNotFoundError("Connection information file not found!")

    with open(connect_fp, mode="r") as connect_file:
        config = json.load(connect_file)

    print ("Kite connection information loaded successfully from file!")

    return config

def login():
    config = load_kite_config()
    http_session = requests.Session()
    url = http_session.get(url='https://kite.trade/connect/login?v=3&api_key='+config["KITE_API_KEY"]).url
    response = http_session.post(url='https://kite.zerodha.com/api/login', data={'user_id':config["USER"], 'password':config["PASSWORD"]})
    resp_dict = json.loads(response.content)
    http_session.post(url='https://kite.zerodha.com/api/twofa', data={'user_id':config["USER"], 'request_id':resp_dict["data"]["request_id"], 'twofa_value':pyotp.TOTP(config["PIN"]).now()})
    url = url + "&skip_session=true"
    response = http_session.get(url=url, allow_redirects=True).url
    request_token = parse_qs(urlparse(response).query)['request_token'][0]

    kite = KiteConnect(api_key=config["KITE_API_KEY"])
    data = kite.generate_session(request_token, api_secret=config["KITE_API_SECRET"])
    kite.set_access_token(data["access_token"])

    return kite

def login_in_zerodha():
    config = load_kite_config()
    api_key = config["KITE_API_KEY"]
    api_secret = config["KITE_API_SECRET"]
    user_id = config["USER"]
    user_pwd = config["PASSWORD"]
    totp_key = config["PIN"]
    driver = uc.Chrome()
    driver.get(f'https://kite.trade/connect/login?api_key={api_key}&v=3')
    login_id = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH, '//*[@id="userid"]'))
    login_id.send_keys(user_id)

    pwd = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH,'//*[@id="password"]'))
    pwd.send_keys(user_pwd)

    submit = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH,'//*[@id="container"]/div/div/div[2]/form/div[4]/button'))
    submit.click()

    time.sleep(5)
    #adjustment to code to include totp
    totp = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH,'//*[@id="userid"]'))
    authkey = pyotp.TOTP(totp_key)
    totp.send_keys(authkey.now())
    #adjustment complete

    time.sleep(15)
    if "request_token" not in driver.current_url:
        continue_btn = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH,'//*[@id="container"]/div/div/div[2]/form/div[3]/button'))
        continue_btn.click()
        time.sleep(15)

    url = driver.current_url
    initial_token = url.split('request_token=')[1]
    request_token = initial_token.split('&')[0]

    driver.close()

    kite = KiteConnect(api_key = api_key)
    #print(request_token)
    data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(data['access_token'])

    return kite

login()
# login_in_zerodha()

