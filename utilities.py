from azure.communication.email import EmailClient
import os
from constants import constants
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import ssl
import requests

def sendemail(lstGoodInstruments, bull=True):
    try:
        connection_string = "endpoint=https://loftynotification.india.communication.azure.com/;accesskey=ewnfBfxcc73nqA+epomtCv9qabIjD5WS9oZV86KO44KfJVlqemVp7s268eyBUWUCuVW3Uz+TOm7m3Om6/CacZw=="
        client = EmailClient.from_connection_string(connection_string)
        
        subject = "Find data attached"
        
        body = ""
        if (len(lstGoodInstruments) == 0):
            subject = "instruments is  are not in specific trend"
            body = "empty or none list of instruments are found to be true"
        else:
            for inst in lstGoodInstruments:
                if (bull):
                    body = body + "BUY " + inst["tradingsymbol"] + " at CMP " + str(inst["last_price"]) + "\n"
                else:
                    body = body + "SELL " + inst["tradingsymbol"] + " at CMP " + str(inst["last_price"]) + "\n"

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

def uploadblob():
    print (constants.TEMPHERE)
    print(requests.certs.where())
    #os.environ["HTTP_PROXY"] = "http://10.10.1.10:1180"
    #os.environ["HTTPS_PROXY"] = "http://10.10.1.10:1180"

    container_name = "lofty-cloud-blobs"
    local_file_name = "access_credentials.json"
    upload_file_path = os.path.join(constants.TEMPHERE, local_file_name)
    STORAGEACCOUNTKEY = "wBuY2m+mdwDXiTF0SsYAhtShctvAwUp1+zgEnnwiTpls17+4NcapbrrnDMLzkE+7HzacqSyKhUFJ+AStf5K4vg=="
    
    account_url = "https://bulionbucket.blob.core.windows.net/lofty-cloud-blobs/access_credentials.json"
    connection_string = "DefaultEndpointsProtocol=https;AccountName=bulionbucket;AccountKey=wBuY2m+mdwDXiTF0SsYAhtShctvAwUp1+zgEnnwiTpls17+4NcapbrrnDMLzkE+7HzacqSyKhUFJ+AStf5K4vg==;EndpointSuffix=core.windows.net"
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Create the Blob Container object
    container = blob_service_client.get_container_client(container=container_name)
    
    blob_client = container.get_blob_client(local_file_name)
    
    if (blob_client.exists()):
        blob_client.delete_blob()
    
    with open(file=upload_file_path, mode="rb") as data:
        blob_client = container.upload_blob(name=local_file_name, data=data, overwrite=False)
 
#uploadblob()