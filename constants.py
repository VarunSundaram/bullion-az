import os
import tempfile
import requests
# TODO: These can be passed in as command line arguments. Make this change later!

class constants:
    
    # Name of file containing app configuration information
    CONNECTION_INFO_FILE_NAME = "connection_info.json"
    
    # Name of file containing configuration information for the logging framework
    LOG_FILE_NAME = "logging.json"

    # Logger for this module
    # LOGGER = logging.getLogger(__name__)
    
    # Name of file access information for the kite api session
    ACCESS = "access_credentials.json"
    
    # Name of file containing instruments under watchlist
    INSTRUMENTS = "instruments.json"
        
    # Get the directory where this python script is being executed
    TEMPHERE = tempfile.gettempdir()
    
    CONTAINER_NAME = "lofty-cloud-blobs"
    
    CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=bulionbucket;AccountKey=wBuY2m+mdwDXiTF0SsYAhtShctvAwUp1+zgEnnwiTpls17+4NcapbrrnDMLzkE+7HzacqSyKhUFJ+AStf5K4vg==;EndpointSuffix=core.windows.net"
    
    STORAGEACCOUNTKEY = "wBuY2m+mdwDXiTF0SsYAhtShctvAwUp1+zgEnnwiTpls17+4NcapbrrnDMLzkE+7HzacqSyKhUFJ+AStf5K4vg=="
    
    STORAGE_ACCOUNT_URL = "https://bulionbucket.blob.core.windows.net/lofty-cloud-blobs/access_credentials.json"
    

#print ("Temporary folder access data json is stored :" + constants.TEMPHERE)

