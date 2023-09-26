from azure.communication.email import EmailClient
import os
from constants import constants
#from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
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


#uploadblob()
