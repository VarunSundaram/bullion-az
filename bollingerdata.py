
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from constants import constants
from kiteconnect import KiteConnect
import os
import json
import math
import utilities as ut

def getDays (days=15):
    previousDay = date.today() - timedelta(days=days)
    currentDay = date.today() + timedelta(days=1)
    
    # %Y-%m-%d %H:%M:%S 2023-09-27 08:37:22
    return previousDay.strftime("%Y-%m-%d"),currentDay.strftime("%Y-%m-%d")

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

def check_movement(dayHistory, move_by):
    low = 0
    last20 = 20
    while low < 2 and last20 > 0:
        # if "20MICRONS-BE" in inst["tradingsymbol"] or "360ONE" in inst["tradingsymbol"]:
        #     print ("hold")

        bollinger, last_price = getMiddle30BBOf(dayHistory, 20)
        
        if last_price < bollinger["mBB"] and move_by == "b":
            low += 1
        elif last_price > bollinger["mBB"] and move_by == "s":
            low += 1
        dayHistory.pop()
        last20 -= 1
    
    return low

def calculateBB():
    ut.start_time = datetime.now()
    api_key, access_token = ut.get_session_token()
    kite = KiteConnect(api_key=api_key, access_token=access_token)
    
    exchange = kite.EXCHANGE_NSE
    instruments = kite.instruments(exchange)
    basecandles = 164
    previousDay,currentDay = getDays(basecandles)
    script = 0
    act_instruments = []
    lst_good_b_Instruments = []
    lst_b_Instruments = []
    lst_good_s_Instruments = []
    lst_s_Instruments = []
    ohlc = []
    day = datetime.now().day
    if (exchange == kite.EXCHANGE_NFO):
        if (day > 22):
            futDate = date.today() + timedelta(days=10)
            futmonth = futDate.strftime("%b").upper()
            futmonth = date.today().strftime("%y") + futmonth + "FUT"
        else:
            futmonth = datetime.now().strftime("%b").upper()
            futmonth = date.today().strftime("%y") + futmonth + "FUT"
        print (futmonth)
    
        for inst in instruments:
            if futmonth in inst["tradingsymbol"]:
                act_instruments.append(inst["tradingsymbol"].replace(futmonth, ""))
                #act_instruments["%03d"%instruments_count] = inst
    else:
        for inst in instruments:
            if inst["tick_size"] == 0.05 and inst["segment"] == "NSE" and inst["lot_size"] == 1:
                act_instruments.append(inst["tradingsymbol"])
    
    print("found as many instruments as {0}".format(len(act_instruments)))
    
    for inst in act_instruments:
        script += 1

        if "NIFTY" in inst:
            continue
        
        try:
            # ohlc = kite.ohlc("NSE:INFY")
            ohlc = kite.ohlc("NSE:"+inst)
        except Exception as ex:
            print ("Exception raised for instrument " +inst + " as  here --" + str(ex))
            if "access_token" in str(ex) and "Incorrect" in str(ex):
                fp = os.path.join(constants.TEMPHERE, constants.ACCESS)
                os.remove(fp)
                fp = os.path.join(constants.TEMPHERE, constants.INSTRUMENTS)
                os.remove(fp)
                return -1
            continue

        if len(ohlc) == 0:
            continue
        
        if ("3PLAND" in inst):
            print ("come here")

        if round(ohlc["NSE:"+inst]["last_price"]) < 80 or round(ohlc["NSE:"+inst]["last_price"]) > 2500:
            continue
        
        if round(ohlc["NSE:"+inst]['ohlc']["open"]) == 0 or round(ohlc["NSE:"+inst]['ohlc']["high"]) == 0 or round(ohlc["NSE:"+inst]['ohlc']["low"]) == 0 or round(ohlc["NSE:"+inst]['ohlc']["close"]) == 0:
            print (inst + " is having either of ohlc as zero")
            continue
            
        # ohlc["NSE:"+inst["tradingsymbol"]]
        dayHistory = kite.historical_data(ohlc["NSE:"+inst]["instrument_token"],
                                previousDay, currentDay, "day")
        
        if len(dayHistory) < 100:
            continue
        
        volume, lstVolume = getVolume(dayHistory)
        
        momVolume = sum(lstVolume) / len(lstVolume)
        baseline_volume = (ohlc["NSE:"+inst]["last_price"] / 50) * 3500
        
        if (baseline_volume > momVolume):
            print ("script {2} has baseline {0} volume is more than minimum volume expectation of {1}".format(baseline_volume, momVolume, inst))
            continue

        low = check_movement(dayHistory, "b")
        
        if low < 2 and (len(lstVolume) - 1) > 0:
            momVolume = sum(lstVolume) / (len(lstVolume) - 1) 
            if len(lstVolume) > 6 and momVolume > (volume * 1.3):
                str_format = {"instrument" : inst, "inst_token": ohlc["NSE:"+inst]["instrument_token"], "last_price": ohlc["NSE:"+inst]["last_price"]}
                lst_good_b_Instruments.append(str_format)
            elif len(lstVolume) > 4 and momVolume > (volume * 1.1):
                str_format = {"instrument" : inst, "inst_token": ohlc["NSE:"+inst]["instrument_token"], "last_price": ohlc["NSE:"+inst]["last_price"]}
                lst_b_Instruments.append(str_format)
        else:
            low = check_movement(dayHistory, "s")
            
            if low < 2 and (len(lstVolume) - 1) > 0:
                momVolume = sum(lstVolume) / (len(lstVolume) - 1) 
                if len(lstVolume) > 6 and momVolume > (volume * 1.3):
                    str_format = {"instrument" : inst, "inst_token": ohlc["NSE:"+inst]["instrument_token"], "last_price": ohlc["NSE:"+inst]["last_price"]}
                    lst_good_s_Instruments.append(str_format)
                elif len(lstVolume) > 4 and momVolume > (volume * 1.1):
                    str_format = {"instrument" : inst, "inst_token": ohlc["NSE:"+inst]["instrument_token"], "last_price": ohlc["NSE:"+inst]["last_price"]}
                    lst_s_Instruments.append(str_format)
            #else:
            #    print ("This instrument is in not in good volume " + str(script) + " : " + inst["tradingsymbol"])

        if (ut.check_elapsed_time()):
            break
    #for inst in lstGoodInstruments:
    #    print ("This instrument is in good uptrend : " + inst["tradingsymbol"])
    #for inst in lstInstruments:
    #    print ("This instrument is in uptrend : " + inst["tradingsymbol"])
    
    #if (exchange == kite.EXCHANGE_NFO):
    ut.create_instrument_file(lst_good_b_Instruments, lst_b_Instruments, lst_good_s_Instruments, lst_s_Instruments)
    # ut.send_email(lst_good_b_Instruments, lst_b_Instruments, lst_good_s_Instruments, lst_s_Instruments)
    
    return 0

# if __name__ == "__main__":
    # fp = os.path.join(Constants.CONFIG_PATH, Constants.ACCESS)
    # with open(fp, 'r') as f:
    #     data = json.load(f)
    
    #kite = KiteConnect(api_key=data["api_key"], access_token=data["access_token"])
    #print (kite.orders())
    #kite.set_access_token(data["access_token"])

