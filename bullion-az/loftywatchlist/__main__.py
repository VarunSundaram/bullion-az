import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from datetime import datetime
import logging
import azure.functions as func

from . import positionaltrading #(relative)

#app = func.FunctionApp() 

#app.register_functions(positionaltrading.pt) 

def main(mytimer: func.TimerRequest) -> None:
    print (datetime.utcnow())
    logging.info (datetime.utcnow())
    #utc_timestamp = datetime.utcnow().replace(
    #    tzinfo=datetime..timezone.utc).isoformat()

    #if mytimer.past_due:
    #    logging.info('The timer is past due!')

    #logging.info('Python timer trigger function ran at %s', utc_timestamp)

    positionaltrading.mainFunction()

#if __name__ == "__main__":
#    positionaltrading.mainFunction()
