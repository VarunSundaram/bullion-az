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
    
    # Name of file containing configuration information for the kite connection information
    ACCESS = "access_credentials.json"
    
    # Get the directory where this python script is being executed
    TEMPHERE = tempfile.gettempdir()

#print ("Temporary folder access data json is stored :" + constants.TEMPHERE)

