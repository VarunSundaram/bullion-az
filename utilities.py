from azure.communication.email import EmailClient
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

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

def connecttoaz():
    container_name = "lofty-cloud-blobs"
    local_file_name = "access_credentials.json"
    upload_file_path = os.path.join(os.path.dirname(__file__), local_file_name)
    
    account_url = "https://bulionbucket.blob.core.windows.net"
    default_credential = DefaultAzureCredential()
    
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    
    # Create the container
    container_client = blob_service_client.create_container(container_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
    
    # Upload the created file
    with open(file=upload_file_path, mode="rb") as data:
        blob_client.upload_blob(data)

#instrument = { "token_name":"INFY", "close": 1350, "mbb": 1352}
#sendemail(instrument)
