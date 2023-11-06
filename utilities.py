#from azure.communication.email import EmailClient
from datetime import date, datetime, timedelta
import os
from constants import constants
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import ssl
import requests
import json
import logging

start_time = ''

def send_email(lst_good_b_instruments, lst_b_instruments, lst_good_s_instruments, lst_s_instruments):
    try:
        connection_string = "endpoint=https://loftynotification.india.communication.azure.com/;accesskey=ewnfBfxcc73nqA+epomtCv9qabIjD5WS9oZV86KO44KfJVlqemVp7s268eyBUWUCuVW3Uz+TOm7m3Om6/CacZw=="
        #client = EmailClient.from_connection_string(connection_string)
        
        subject = "Find data attached"
        
        body = ""
        if (len(lst_good_b_instruments) == 0 and len(lst_b_instruments) == 0 and len(lst_good_s_instruments) == 0 and len(lst_s_instruments) == 0):
            subject = "instruments is  are not in specific trend"
            body = "empty or none list of instruments are found to be true"
        else:
            for inst in lst_good_b_instruments:
                body = body + "good BUY " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"
            for inst in lst_good_s_instruments:
                body = body + "good SELL " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"
            for inst in lst_good_b_instruments:
                body = body + "BUY " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"
            for inst in lst_good_s_instruments:
                body = body + "SELL " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"

        message = {
            "senderAddress": "DoNotReply@da760745-49f2-4ccf-8808-111916272d1a.azurecomm.net",
            "recipients":  {
                "to": [{"address": "varunsundaram@outlook.com" }],
            },
            "content": {
                "subject": subject,
                "plainText": body,
            }
        }

        #poller = client.begin_send(message)
        #result = poller.result()

    except Exception as ex:
        print (ex)
        return ex

def get_blob_client(local_file_name):
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(constants.CONNECTION_STRING)
    
    # Create the Blob Container object
    container = blob_service_client.get_container_client(container=constants.CONTAINER_NAME)
    
    blob_client = container.get_blob_client(local_file_name)
    return container,blob_client


def upload_blob(local_file_name = "access_credentials.json"):
    if ("22557" in str(constants.TEMPHERE)):
        return
    print (constants.TEMPHERE)
    print(requests.certs.where())
    #os.environ["HTTP_PROXY"] = "http://10.10.1.10:1180"
    #os.environ["HTTPS_PROXY"] = "http://10.10.1.10:1180"

    upload_file_path = os.path.join(constants.TEMPHERE, local_file_name)
    ssl._create_default_https_context = ssl._create_unverified_context
    
    container, blob_client = get_blob_client(local_file_name)
    
    if (blob_client.exists()):
        logging.info('before uploding blob delete old blob name %s', local_file_name)
        blob_client.delete_blob()
    
    with open(file=upload_file_path, mode="rb") as data:
        blob_client = container.upload_blob(name=local_file_name, data=data, overwrite=False)

def check_blob(local_file_name = constants.ACCESS):
    if ("22557" in str(constants.TEMPHERE)):
        return True
    ssl._create_default_https_context = ssl._create_unverified_context
    
    container, blob_client = get_blob_client(local_file_name)
    return blob_client.exists()
 
def delete_blob(local_file_name = constants.ACCESS):
    if ("22557" in str(constants.TEMPHERE)):
        return
    ssl._create_default_https_context = ssl._create_unverified_context
    
    container, blob_client = get_blob_client(local_file_name)
    if (blob_client.exists()):
        logging.info('delete blob name %s', local_file_name)
        blob_client.delete_blob()
    else:
        logging.info('blob name {0} not found to delete'.format(local_file_name))

def download_blob(local_file_name = constants.ACCESS):
    if ("22557" in str(constants.TEMPHERE)):
        print ("in local debug session..")
        fp = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
        if not os.path.isfile(fp):
            return 1
        return 0
    #try:
    download_file_path = os.path.join(constants.TEMPHERE, local_file_name)
    ssl._create_default_https_context = ssl._create_unverified_context
    
    container, blob_client = get_blob_client(local_file_name)
    
    if (blob_client.exists()):
        blob_properties = blob_client.get_blob_properties()
        
        logging.info('download blob name {0} which is created on {1}'.format(local_file_name, blob_properties.creation_time))
        bytes = blob_client.download_blob().readall()
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
        with open(download_file_path, "wb") as file:
            file.write(bytes)
        return 0
    else:
        logging.info('blob name {0} not found for download'.format(local_file_name))
        
    return -1
    #except Exception as ex:
    #        print ("Exception raised for blob as  here --" + str(ex))
        
def create_instrument_file(lst_good_b_Instruments, lst_b_Instruments, lst_good_s_Instruments, lst_s_Instruments):
    instrument_file_path = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
    # Serializing json  
    
    if (len(lst_good_b_Instruments) == 0 and len(lst_b_Instruments) == 0 and len(lst_good_s_Instruments) == 0 and len(lst_s_Instruments) == 0):
        delete_blob(constants.INSTRUMENTS)
        return
    
    final_list = { "good buy" : lst_good_b_Instruments, "buy" : lst_b_Instruments, "good sell" : lst_good_s_Instruments, "sell" : lst_s_Instruments }
    json_object = json.dumps(final_list, indent = 4) 
    
    # Writing to sample.json
    with open(instrument_file_path, "w+") as outfile:
        outfile.write(json_object)
        
    upload_blob(constants.INSTRUMENTS)

def get_session_token():
    """
    get kite session token
    :return: api_key and access_token
    :rtype: string
    """
    fp = os.path.join(constants.TEMPHERE, constants.ACCESS)
    with open(fp, 'r') as f:
        data = json.load(f)
    
    return data["api_key"], data["access_token"]

def check_elapsed_time():
    stop = datetime.now()
    elapsed = stop - start_time
    #hour = datetime.utcnow().hour

    if elapsed >= timedelta(seconds=570):
    #if hour >= 10:
        logging.info ("Slept for > 9 minute in ticker function with elapsed time {0}".format(elapsed))
        print ("Slept for > 9 minute in ticker function with elapsed time {0}".format(elapsed))
        return True # modified to false for now
    else:
        return False

#uploadblob()
#download_blob()