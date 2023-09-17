import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from kiteconnect import KiteConnect
import os
import json
import math
from . import Constants

def getDays (days=15):
    previousDay = date.today() - timedelta(days=days)
    currentDay = date.today() + timedelta(days=1)
    
    # %Y-%m-%d %H:%M:%S 2023-09-27 08:37:22
    return previousDay.strftime("%Y-%m-%d"),currentDay.strftime("%Y-%m-%d")

def calculateBB(kite):
    instruments = kite.instruments(kite.EXCHANGE_NSE)
    basecandles = 164
    previousDay,currentDay = getDays(basecandles)
    script = 0
    lstGoodInstruments = []
    lstInstruments = []
    for inst in instruments:
        script += 1

        if "NIFTY" in inst["tradingsymbol"]:
            continue
        
        # ohlc = kite.ohlc("NSE:INFY")
        ohlc = kite.ohlc("NSE:"+inst["tradingsymbol"])

        if len(ohlc) == 0:
            continue

        if ohlc["NSE:"+inst["tradingsymbol"]]["last_price"] < 60:
            continue
        # ohlc["NSE:"+inst["tradingsymbol"]]
        dayHistory = kite.historical_data(inst["instrument_token"],
                                previousDay, currentDay, "day")
        
        if len(dayHistory) < 100:
            continue
        
        low = 0
        last20 = 20
        volume, lstVolume = getVolume(dayHistory)

        while low < 2 and last20 > 0:
            # if "20MICRONS-BE" in inst["tradingsymbol"] or "360ONE" in inst["tradingsymbol"]:
            #     print ("hold")

            bollinger, last_price = getMiddle30BBOf(dayHistory, 20)
            
            if last_price < bollinger["mBB"]:
                low += 1
            dayHistory.pop()
            last20 -= 1

        if low < 2 and (len(lstVolume) - 1) > 0:
            momVolume = sum(lstVolume) / (len(lstVolume) - 1)
            if len(lstVolume) > 6 and momVolume > (volume * 1.3):
                lstGoodInstruments.append(inst)
            elif len(lstVolume) > 4 and momVolume > (volume * 1.1):
                lstInstruments.append(inst)
            #else:
            #    print ("This instrument is in not in good volume " + str(script) + " : " + inst["tradingsymbol"])

    for inst in lstGoodInstruments:
        print ("This instrument is in good uptrend : " + inst["tradingsymbol"])
    for inst in lstInstruments:
        print ("This instrument is in uptrend : " + inst["tradingsymbol"])

def getVolume(dayHistory, basecounter=20):

    lstVolume = { 0 }
    counter = 0
    notrade = 0
    volume = 0
    for candle in reversed(dayHistory):
        volume = volume + candle["volume"]
        if (candle["close"] > candle["open"]):
            lstVolume.add(candle["volume"])
        if (candle["close"] == candle["open"]):
            notrade += 1
        counter += 1
        if counter == basecounter:
            break
    volume = volume / basecounter
    if notrade > 3:
        lstVolume = { 0 }
    return volume, lstVolume

def getMiddle30BBOf(dayHistory, basecandles = 20):
    
    mBB = 0
    candleCount = 0
    last_price = 0
    for candle in reversed(dayHistory):
        mBB = mBB + candle["close"]
        if last_price == 0:
            last_price = candle["close"]
        candleCount += 1
        if candleCount == basecandles:
            break
    mBB = round(mBB / basecandles, 2)
    candleCount = 0
    sd = 0
    for candle in reversed(dayHistory):
        sd = (mBB -  candle["close"]) * (mBB -  candle["close"]) + sd
        candleCount += 1
        if candleCount == basecandles:
            break
    sd = round(math.sqrt(sd/candleCount), 2) * 2
    bollinger = {"mBB" : mBB, "uBB" : mBB + sd, "lBB" : mBB - sd}

    return bollinger, last_price

# if __name__ == "__main__":
    # fp = os.path.join(Constants.CONFIG_PATH, Constants.ACCESS)
    # with open(fp, 'r') as f:
    #     data = json.load(f)
    
    #kite = KiteConnect(api_key=data["api_key"], access_token=data["access_token"])
    #print (kite.orders())
    #kite.set_access_token(data["access_token"])

    