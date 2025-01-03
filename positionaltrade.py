from http import HTTPStatus
import json
#import logmatic
import logging
import requests
import re
import os

from datetime import datetime, timedelta
import pyotp
from kiteconnect import KiteConnect
from constants import constants #(relative)
import utilities as ut
import ticker
import bollingerdata as bd
import time
import subprocess

__author__ = "Varun kumar Sundaram"

kite = ''

def load_kite_config():
    """
    Load the kite configuration information from the json file
    :return: A python dictionary
    :rtype: dict
    """
    connect_fp = os.path.join(os.path.dirname(__file__), constants.CONNECTION_INFO_FILE_NAME)

    if not os.path.exists(connect_fp):
        raise FileNotFoundError("Connection information file not found!")

    with open(connect_fp, mode="r") as connect_file:
        config = json.load(connect_file)

    print ("Kite connection information loaded successfully from file!")

    return config

def need_to_generate_token():
    exit_code = ut.download_blob()
    flag = False
    fp = os.path.join(constants.TEMPHERE, constants.ACCESS)
        
    login_time=''
    if os.path.isfile(fp):
        print (constants.ACCESS + " present in temporary folder")
        with open(fp, 'r') as f:
            data = json.load(f)
        logging.info ("Previous login time for "+data["user_name"]+" is "+str(data["login_time"]))
        login_time = datetime.strptime(data["login_time"],"%Y-%m-%d %H:%M:%S")
        login_time = login_time + timedelta(days=1)
        cut_off_time = datetime(login_time.year,login_time.month,login_time.day,2,00,00)
        if datetime.now() < cut_off_time and "access_token" in data.keys():
            logging.info ("Acces token is fresh")
        else:
            os.remove(fp)
            logging.info (constants.ACCESS+" has been deleted.")
            flag=True
    else:
        if os.path.isfile(fp) and exit_code == -1:
            os.remove(fp)
            logging.info (constants.ACCESS+" deleted from local folder")
        else:
            logging.info (constants.ACCESS+" does not exist in current folder")
        flag = True
    return flag,login_time

def kite_prelogin(config, http_session):
    """
    Perform pre-login into kite
    :param config: The python dictionary containing kite configuration information
    :type config: dict
    :param http_session: A http session
    :type http_session: :class:`requests.Session`
    :return: The response referer url
    :rtype: str
    """
    url = config["LOGIN_REFERER"] + config["KITE_API_KEY"]

    response = http_session.get(url=url)

    return response.url


def login_kite(config, http_session):
    """
    Perform a login
    :param config: The python dictionary containing kite configuration information
    :type config: dict
    :param http_session: A http session
    :type http_session: :class:`requests.Session`
    :return: The response payload as a python dictionary
    :rtype: dict
    """

    url = config["LOGIN_URL"]
    data = dict()
    data["user_id"] = config["USER"]
    data["password"] = config["PASSWORD"]
    response = http_session.post(url=url, data=data)
    
    # Deserialize the response content
    resp_dict = json.loads(response.content)

    if "message" in resp_dict.keys():
        # Since logging framework already expects message as a parameter change the key
        resp_dict["err_message"] = resp_dict["message"]
        del resp_dict["message"]

    if response.status_code != HTTPStatus.OK:
        logging.info ("Login failure", extra=resp_dict)
        print ("Login failure", extra=resp_dict)
        raise ConnectionError("Login failed!")

    return resp_dict


def kite_twofa(login_resp, config, http_session):
    """
    Perform kite-two-factor authentication
    :param login_resp: The response payload from the primary user login
    :type login_resp: dict
    :param config: The python dictionary containing kite configuration information
    :type config: dict
    :param http_session: A http session
    :type http_session: :class:`requests.Session`
    :return: The response payload as a python dictionary
    :rtype: dict
    """
    url = config["TWOFA_URL"]
    data = dict()
    data["user_id"] = config["USER"]
    data["request_id"] = login_resp["data"]["request_id"]
    data["twofa_value"] = str(pyotp.TOTP(config["PIN"]).now())

    response = http_session.post(url=url, data=data)

    # Deserialize the response content
    resp_dict = json.loads(response.content)
    

    if "message" in resp_dict.keys():
        # Since logging framework already expects message as a parameter change the key
        resp_dict["err_message"] = resp_dict["message"]
        del resp_dict["message"]

    if response.status_code != HTTPStatus.OK:
        print ("Two-factor authentication failure", extra=resp_dict)
        raise ConnectionError("Two-factor authentication failed!")

    return resp_dict

def kite_post_twofa(url,  http_session):
    """
    Perform action after kite-two-factor authentication
    :param login_resp: The response payload from the primary user login
    :type login_resp: dict
    :param http_session: A http session
    :type http_session: :class:`requests.Session`
    :return: The response payload as a python dictionary
    :rtype: dict
    """
    url = url+"&skip_session=true"
    # print ("Post TwoFA url " + url)

    try:
        response = http_session.get(url=url, allow_redirects=True, verify=False)
        if response.status_code == 302:
            reply = response.headers["Location"]
            request_token = re.findall(r'request_token=(.*)&action',reply)[0]
    except Exception as e:
        logging.info ("in post 2fa expcetion block..")
        pat = re.compile(r'request_token=(.*?)\s+')
        request_token = re.search(pat, str(e)).group(1).strip()
        request_token = request_token.split('&')[0]
    
    # Deserialize the response content
    return request_token

def generate_access_token(config,request_token):
    fp = os.path.join(constants.TEMPHERE, constants.ACCESS)
    kite = KiteConnect(api_key=config["KITE_API_KEY"])
    data = kite.generate_session(request_token, api_secret=config["KITE_API_SECRET"])
    if "request_token" in data.keys():
        del data["request_token"]
        del data["refresh_token"]
        logging.info ("deleted old request token")
    data["request_token"] = request_token

    user_data = json.dumps(data, indent=4, sort_keys=True, default=str)
    # logging.info (data["access_token"])
    print (data["user_name"],data["login_time"],data["access_token"])

    with open(fp, "w") as outfile:
        outfile.write(user_data)
    #time.sleep(5)
    kite.set_access_token(data["access_token"])
    logging.info ("Automatic login for "+data["user_name"]+" is done. "+constants.ACCESS+" has been written to disk")
    return kite

def start_session():
    # Initialize logging framework
    # init_logging()
    
    hour = datetime.utcnow().hour
    if hour >= 20 or hour <= 2:
        print ("do nothing")
        return
    elif hour >= 19 :
        fp = os.path.join(constants.TEMPHERE, constants.ACCESS)
        if os.path.isfile(fp):
            os.remove(fp)
        fp = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
        if os.path.isfile(fp):
            os.remove(fp)
        ut.delete_blob(constants.ACCESS)
        ut.delete_blob(constants.INSTRUMENTS)
        return
    elif hour <= 3:
        if (ut.download_blob(constants.INSTRUMENTS) == 0):
            minute = datetime.utcnow().minute
            logging.info('Instruments is already there')
            if minute < 10:
                logging.info('Instruments must be deleted and hence proceeding')
                ut.delete_blob(constants.INSTRUMENTS)
            return
        create_new_session()
        
        logging.info('calculating bollinger data')
        exit_code = bd.calculateBB()
        return
    elif hour >= 4 and hour <= 9:
        create_new_session() # uncomment only during debug session
        
        if (ut.download_blob(constants.INSTRUMENTS) == 0):
            # start_new_process()
            ticker.start_ticker()
        else:
            logging.info ('calculating bb again as Instruments not found')
            bd.calculateBB()

        return

def create_new_session():
    # Load the kite configuration information
    kite_config = load_kite_config()

    sess = requests.Session()

    # Attempt pre-login
    ref_url = kite_prelogin(config=kite_config, http_session=sess)

    # Attempt a login and get the response as a dictionary
    user_pass_login_resp = login_kite(config=kite_config, http_session=sess)
    logging.info ("Login successful!")

    # Attempt two-factor auth
    two_fa_resp = kite_twofa(login_resp=user_pass_login_resp, config=kite_config, http_session=sess)
    #LOGGER.info("Two-factor authentication passed!", extra=two_fa_resp)
    request_token = kite_post_twofa(url=ref_url,http_session=sess)
    print ("Generated request token = %s".format(str(request_token)))

    kite = generate_access_token(kite_config,request_token)
    return kite

def start_new_process():
    logging.info ('going into ticker operation')
    output = subprocess.check_output(["pwd"], text=True)
    logging.info ("value return subprocess command.. " + str(output))
    output = subprocess.check_output(["python", "--version"], text=True)
    logging.info ("value return subprocess command.. " + str(output))
    output = subprocess.check_output(["ls", "-l"], text=True)
    logging.info ("value return subprocess command.. " + str(output))
    fp = os.path.join(os.curdir, "execute_ticker.sh")
    if os.path.isfile(fp):
        logging.info ("Execute ticker shell file is found ")
    else:
        logging.info ("Execute ticker shell file is NOT----TTTTT found ")
    result = subprocess.run(["sh", "./execute_ticker.sh"], capture_output=True)
    #result = subprocess.run(["python", "ticker.py"], capture_output=True)
    logging.info ("Exit Code of the subprocess wait.. " + str(result))
    logging.info ("1 Exit Code of the subprocess wait.. " + str(result.returncode))
    

if __name__ == "__main__":
    start_session()
