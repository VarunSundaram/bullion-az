from kiteconnect import KiteTicker
from kiteconnect import KiteConnect

import logging
import os
from constants import constants
import json
from datetime import datetime, timedelta
import bollingerdata as bd
import time
import utilities as ut

#logging.basicConfig(level=logging.DEBUG)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    for tick_data in ticks:
        print ("Ticks: token : {0}, last_price : {1}, volume : {2}".format(str(tick_data["instrument_token"]), str(tick_data["last_price"]), str(tick_data["volume_traded"]))  )    

def on_connect(ws, response):
    # Callback on successful connect.
    connect_fp = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)

    with open(connect_fp, mode="r") as connect_file:
        instruments = json.load(connect_file)
    
    inst_list = instruments["good buy"] + instruments["buy"]
    ticker_inst = []
    for inst in inst_list:
        ticker_inst.append(inst["inst_token"])
    
    print ([260105,256265])
    print (ticker_inst)
    ws.subscribe(ticker_inst)

    # Set all instruments to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, ticker_inst)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    logging.info ("Websocket Error Code: ", code)
    logging.info ("Reason: ", reason)
    if "access_token" in str(reason) and "Incorrect" in str(reason):
        ut.delete_blob(constants.ACCESS)
        ut.delete_blob(constants.INSTRUMENTS)
    ws.stop()

def on_error(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will happen after executing `ws.error()`
    logging.info ("on_error while connecting kite to --" + str(reason))
    if "access_token" in str(reason) and "Incorrect" in str(reason):
        ut.delete_blob(constants.ACCESS)
        ut.delete_blob(constants.INSTRUMENTS)


def on_reconnect(ws, code, reason):
    print ("on reconnect")

def start_ticker(api_key, kite):
    ut.download_blob(constants.INSTRUMENTS)
    
    # Initialise
    kws = KiteTicker(api_key, kite.access_token) # debug=True
    start = datetime.now()
    
    # Assign the callbacks.
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error

    # Infinite loop on the main thread. Nothing after this will run.
    # You have to use the pre-defined callbacks to manage subscriptions.
    kws.connect()
    
    while True:
        time.sleep(1)
        stop = datetime.now()
        elapsed = stop - start

        if elapsed >= timedelta(minutes=9):
            logging.info ("Slept for > 9 minute")
            break
        