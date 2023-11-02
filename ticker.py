from kiteconnect import KiteTicker
from kiteconnect import KiteConnect

import logging
import os
import random
from constants import constants
import json
from datetime import datetime, timedelta
import bollingerdata as bd
import time
import utilities as ut

#logging.basicConfig(level=logging.DEBUG)

def get_ticker_inst():
    logging.info ("get ticker instruments event triggered")
    # Callback on successful connect.
    connect_fp = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
    
    if os.path.isfile(connect_fp):
        logging.info ("instrument.json file is found")
    else:
        logging.info ("Self raised Exception : instrument.json file is not found")
        raise Exception("Exception: instrument file is not found in temp folder")
    
    with open(connect_fp, mode="r") as connect_file:
        instruments = json.load(connect_file)
    
    inst_list = []
    if "good buy" in instruments:
        inst_list = inst_list + instruments["good buy"]
    if "buy" in instruments:
        inst_list = inst_list + instruments["buy"]
    if "good sell" in instruments:
        inst_list = inst_list + instruments["good sell"]
    if "sell" in instruments:
        inst_list = inst_list + instruments["sell"]
    
    ticker_inst = []
    for inst in inst_list:
        ticker_inst.append(inst["inst_token"])
    
    logging.info ("get ticker instruments event ended")
    return ticker_inst


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    tick_data = random.choice(ticks)
    #for tick_data in ticks:
    #   logging.info ("Ticks: token : {0}, last_price : {1}, volume : {2}".format(str(tick_data["instrument_token"]), str(tick_data["last_price"]), str(tick_data["volume_traded"]))  )    
    #   break
    check_ticker(ws, ticks)

def on_connect(ws, response):
    try:
        logging.info ("on_connect event triggered")
        ticker_inst = get_ticker_inst()
        #print ([260105,256265])
        logging.info (ticker_inst)
        ws.subscribe (ticker_inst)
        
        # Set all instruments to tick in `full` mode.
        ws.set_mode(ws.MODE_FULL, ticker_inst)
        logging.info ("on_connect event ended")
    except Exception as ex:
        logging.info ("Exception raised during ticker.connect() as --" + str(ex))
        raise Exception(ex)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    logging.info ("on_close event triggered")
    ticker_inst = get_ticker_inst()
    logging.info (ticker_inst)
    ws.unsubscribe (ticker_inst)
    time.sleep(3)
    
    # Reconnection will not happen after executing `ws.stop()`
    logging.info ("Websocket Error Code: {0} and reason {1}".format(code, reason))
    print ("Websocket Error Code: {0} and reason {1}".format(code, reason))
    ws.stop()
    if "access_token" in str(reason) and "Incorrect" in str(reason):
        ut.delete_blob(constants.ACCESS)
        ut.delete_blob(constants.INSTRUMENTS)
    
    logging.info ("on_close event ended")

def on_error(ws, code, reason):
    logging.info ("on_error event triggered")
    # On connection close stop the main loop
    # Reconnection will happen after executing `ws.error()`
    logging.info ("on_error while connecting kite to --" + str(reason))
    print ("on_error while connecting kite to --" + str(reason))
    if "access_token" in str(reason) and "Incorrect" in str(reason):
        ut.delete_blob(constants.ACCESS)
        ut.delete_blob(constants.INSTRUMENTS)
    
    ws.close()
    logging.info ("on_close event ended")

def on_reconnect(ws, code, reason):
    logging.info ("on reconnect")

def start_ticker(api_key, access_token):
    connect_fp = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
    
    if os.path.isfile(connect_fp):
        logging.info ('instrument is already there. no need to dwonload again')
    else:
        logging.info ('instrument is not found in temp folder. Assuming previous download failed')
        exit_code = ut.download_blob(constants.INSTRUMENTS)
    
        if (exit_code == -1):
            logging.info('Session Failed. So deleting blob to try new')
            print ('Session Failed. So deleting blob to try new')
            ut.delete_blob()
            return
    
    # ticker_inst = get_ticker_inst() # check for ticker list subscription data
    
    # Initialise
    kws = KiteTicker(api_key, access_token) # debug=True
    
    # Assign the callbacks.
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error

    # Infinite loop on the main thread. Nothing after this will run.
    # You have to use the pre-defined callbacks to manage subscriptions
    try:
        logging.info ('Connecting to kite ticker..')
        kws.connect(threaded=True)
        #kws.connect()
        while True:
            time.sleep(1)
            if check_thread_timer():
                ticker_inst = get_ticker_inst()
                logging.info (ticker_inst)
                kws.unsubscribe (ticker_inst)
                time.sleep(3)
                kws.close()
                return
    except Exception as ex:
        logging.info ("Exception raised during kite.connect() as --" + str(ex))
        raise (ex)

def check_thread_timer():
    stop = datetime.now()
    elapsed = stop - ut.start_time
    #hour = datetime.utcnow().hour

    if elapsed >= timedelta(seconds=570):
    #if hour >= 10:
        logging.info ("Slept for > 9 minute in ticker function with elapsed time {0}".format(elapsed))
        print ("Slept for > 9 minute in ticker function with elapsed time {0}".format(elapsed))
        # ticker_inst = get_ticker_inst()
        # logging.info (ticker_inst)
        # ws.unsubscribe (ticker_inst)
        # time.sleep(3)
        
        return True
    else:
        print ("waiting to close connexion with time {0}".format(elapsed))
        return False

def check_ticker(ws, ticks):
    if check_thread_timer():
        #ws.close()
        logging.info ("In ticker thread with > 9 minute  elapsed time {0}".format(datetime.now()))
