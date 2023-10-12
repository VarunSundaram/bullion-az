from azure.communication.email import EmailClient
import os
from constants import constants
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import ssl
import requests
import json
import logging

start_time = ''

def send_email(lstGoodInstruments, lst_instruments, bull=True):
    try:
        connection_string = "endpoint=https://loftynotification.india.communication.azure.com/;accesskey=ewnfBfxcc73nqA+epomtCv9qabIjD5WS9oZV86KO44KfJVlqemVp7s268eyBUWUCuVW3Uz+TOm7m3Om6/CacZw=="
        client = EmailClient.from_connection_string(connection_string)
        
        subject = "Find data attached"
        
        body = ""
        if (len(lstGoodInstruments) == 0 and len(lst_instruments) == 0):
            subject = "instruments is  are not in specific trend"
            body = "empty or none list of instruments are found to be true"
        else:
            for inst in lstGoodInstruments:
                if (bull):
                    body = body + "good BUY " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"
                else:
                    body = body + "good SELL " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"
            for inst in lst_instruments:
                if (bull):
                    body = body + "BUY " + inst["instrument"] + " at CMP " + str(inst["last_price"]) + "\n"
                else:
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

        poller = client.begin_send(message)
        result = poller.result()

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
        return 0
    #try:
    download_file_path = os.path.join(constants.TEMPHERE, local_file_name)
    ssl._create_default_https_context = ssl._create_unverified_context
    
    container, blob_client = get_blob_client(local_file_name)
    
    if (blob_client.exists()):
        logging.info('download blob name %s', local_file_name)
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
        
def create_instrument_file(lstgoodinstruments, lst_instruments):
    instrument_file_path = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
    # Serializing json  
    
    if (len(lstgoodinstruments) == 0 and len(lst_instruments) == 0):
        delete_blob(constants.INSTRUMENTS)
        return
    
    final_list = { "good buy" : lstgoodinstruments, "buy" : lst_instruments }
    json_object = json.dumps(final_list, indent = 4) 
    
    # Writing to sample.json
    with open(instrument_file_path, "w+") as outfile:
        outfile.write(json_object)
        
    upload_blob(constants.INSTRUMENTS)

#uploadblob()
#download_blob()