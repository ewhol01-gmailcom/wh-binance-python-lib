import hmac
import time
import hashlib
from binance_f.model.constant import WorkingType
import requests
import json
from urllib.parse import urlencode

import sys
import pprint

KEY = '4Eiv4LT3Ci85P4seGXIV7N4a4JrvUY3zNTar37MvC96HQPFaLaTjqiInv1NznQo6'
SECRET = 'kZm9NdZ6cnh4q1DildKj7DJJL37K7Si58GvTeBvIgOORsEQ2lle1feCKGtvyMjJE'
BASE_URL = 'https://fapi.binance.com' # production base url
# BASE_URL = 'https://testnet.binancefuture.com' # testnet base url

''' ======  begin of functions, you don't need to touch ====== '''
def hashing(query_string):
    return hmac.new(SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_timestamp():
    return int(time.time() * 1000)

def dispatch_request(http_method):
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json;charset=utf-8',
        'X-MBX-APIKEY': KEY
    })
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post,
    }.get(http_method, 'GET')

# used for sending request requires the signature
def send_signed_request(http_method, url_path, payload={}, verbose=False):
    query_string = urlencode(payload)
    # replace single quote to double quote
    query_string = query_string.replace('%27', '%22')
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, get_timestamp())
    else:
        query_string = 'timestamp={}'.format(get_timestamp())

    url = BASE_URL + url_path + '?' + query_string + '&signature=' + hashing(query_string)
    if verbose:
        print("{} {}".format(http_method, url))
    params = {'url': url, 'params': {}}
    response = dispatch_request(http_method)(**params)
    return response.json()

# used for sending public data request
def send_public_request(url_path, payload={}, verbose=False):
    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + '?' + query_string
    if verbose:
        print("{}".format(url))
    response = dispatch_request('GET')(url=url)
    return response.json()

''' ======  end of functions ====== '''

def _wh_send_order(symbol="DOGEUSDT",
                    side="BUY/SELL",
                    positionSide="LONG/SHORT",
                    type="LIMIT/MARKET/STOP/TAKE_PROFIT/STOP_MARKET/TAKE_PROFIT_MARKET/TRAILING_STOP_MARKET",
                    quantity=0,
                    stopPrice=0,
                    closePosition="FALSE",
                    workingType="MARK_PRICE/CONTRACT_PRICE",
                    priceProtect="TRUE", 
                    verbose=False
                    ):
    # if symbol=="" or side=="" or type=="":
    #     print("Usage:")
    #     print('wh_send_order(symbol="DOGEUSDT",side="BUY/SELL",positionSide="LONG/SHORT",'+
    #             'type="LIMIT/MARKET/STOP/TAKE_PROFIT/STOP_MARKET/TAKE_PROFIT_MARKET/TRAILING_STOP_MARKET",'+
    #             'quantity=0,stopPrice=0,closePosition="FALSE",workingType="MARK_PRICE/CONTRACT_PRICE",priceProtect="TRUE"')
    #     return(False)
    if workingType=="MARK_PRICE/CONTRACT_PRICE":
        workingType="MARK_PRICE"
    params = {
        "symbol" : symbol,
        "side" : side,
        "positionSide" : positionSide,
        "type" : type,
        "quantity" : quantity,
        "stopPrice" : stopPrice,
        "closePosition" : closePosition,
        "workingType" : workingType,
        "priceProtect" : priceProtect
    }
    r = send_signed_request("POST","/fapi/v1/order",params, verbose)
    return(r)

# wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="LONG",type="STOP_MARKET",quantity=1,stopPrice=0.5) #open order, buy above price
# wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="LONG",type="TAKE_PROFIT_MARKET",quantity=1,stopPrice=0.11) #open order, buy below price
# wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="SHORT",type="STOP_MARKET",quantity=1,stopPrice=0.11) #open order, sell below price
# wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="SHORT",type="TAKE_PROFIT_MARKET",quantity=1,stopPrice=0.51) #open order, sell above price

# wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="LONG",type="TAKE_PROFIT_MARKET",quantity=1,stopPrice=0.51) #open order close long above price
# wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="LONG",type="STOP_MARKET",quantity=1,stopPrice=0.11) #open order close long below price
# wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="SHORT",type="TAKE_PROFIT_MARKET",quantity=1,stopPrice=0.11) #open order close short below price
# wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="SHORT",type="STOP_MARKET",quantity=1,stopPrice=0.51) #open order close short above price

def get_current_price(symbol="DOGEUSDT", verbose=False):
    params = {
        "symbol" : symbol,
        "interval" : "1d",
        "limit" : 1
    }
    r = send_signed_request("GET","/fapi/v1/markPriceKlines",params,verbose)
    if verbose:
        print(r)
    return(float(r[0][4]))

def wh_send_order(symbol="DOGEUSDT",side="BUY",type="OPEN",price=0,quantity=0,workingType="MARK_PRICE/CONTRACT_PRICE",priceProtect="TRUE",verbose=False):
    pricePrecision, quantityPrecision = get_pair_precisions(symbol)
    cp = get_current_price()
    if verbose:
        print(symbol,side,type,price,quantity,"{:0.0{}f}".format(price,pricePrecision),"{:0.0{}f}".format(quantity,quantityPrecision))
    if side=="BUY":
        if type=="OPEN":
            if price<cp: #open buy below price
                r = _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="LONG",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order, buy below price
            elif price>cp: #open buy above price
                r = _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="LONG",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order, buy above price
        elif type=="CLOSE":
            if price<cp: #close buy below price
                r = _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="SHORT",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order close short below price            
            elif price>cp: #close buy above price
                r= _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="SHORT",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order close short above price    elif side=="SELL":
    elif side=="SELL":
        if type=="OPEN":
            if price<cp: #open sell below price
                r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="SHORT",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order, sell below price
            elif price>cp: #open sell above price
                r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="SHORT",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order, sell above price
        elif type=="CLOSE":
            if price<cp: #close sell below price
                r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="LONG",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order close long below price
            elif price>cp: #close sell above price
                r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="LONG",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    verbose=verbose) #open order close long above price
    if verbose:
        print(r)
    return

# previous version:
# def wh_send_order(symbol="DOGEUSDT",side="BUY",type="OPEN",price=0,quantity=0,workingType="MARK_PRICE/CONTRACT_PRICE",priceProtect="TRUE",verbose=False):
#     pricePrecision, quantityPrecision = get_pair_precisions(symbol)
#     cp = get_current_price()
#     if side=="BUY":
#         if type=="OPEN":
#             if price<cp: #open buy below price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="LONG",
#                     type="TAKE_PROFIT_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order, buy below price
#             elif price>cp: #open buy above price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="LONG",
#                     type="STOP_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order, buy above price
#         elif type=="CLOSE":
#             if price<cp: #close buy below price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="SHORT",
#                     type="TAKE_PROFIT_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order close short below price            
#             elif price>cp: #close buy above price
#                 r= _wh_send_order(symbol="DOGEUSDT",side="BUY",positionSide="SHORT",
#                     type="STOP_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order close short above price    elif side=="SELL":
#     elif side=="SELL":
#         if type=="OPEN":
#             if price<cp: #open sell below price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="SHORT",
#                     type="STOP_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order, sell below price
#             elif price>cp: #open sell above price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="SHORT",
#                     type="TAKE_PROFIT_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order, sell above price
#         elif type=="CLOSE":
#             if price<cp: #close sell below price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="LONG",
#                     type="STOP_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order close long below price
#             elif price>cp: #close sell above price
#                 r = _wh_send_order(symbol="DOGEUSDT",side="SELL",positionSide="LONG",
#                     type="TAKE_PROFIT_MARKET",quantity=quantity,stopPrice=price,verbose=verbose) #open order close long above price
#     if verbose:
#         print(r)
#     return

def get_account_balance_v2(symbol="",simple=False,verbose=False):
    r = send_signed_request("GET","/fapi/v2/balance")
    if verbose:
        print(r)
    if symbol!="":
        for a in r:
            if a["asset"]==symbol:
                return(a["availableBalance"])
    if simple:
        b = []
        for a in r:
            b.append([a["asset"],a["availableBalance"]])
        return(b)
    return(r)

def get_exchange_info(verbose=False):
    r = send_signed_request("GET","/fapi/v1/exchangeInfo")
    if verbose:
        print(r)
    return(r)

def get_pair_precisions(pair="DOGEUSDT",verbose=False):
    exin = get_exchange_info()

    # print(exin.symbols[0].symbol)
    # search precisions for symbol=pair
    res = None
    for sym in exin["symbols"]:
        if sym["symbol"] == pair:
            res = sym
            break
    if verbose:
        print("Precisions for",pair,":")
        print("Price precision =",res["pricePrecision"])
        print("Quantity precision =",res["quantityPrecision"])
        print("Base asset precision =",res["baseAssetPrecision"])
        print("Quote precision =",res["quotePrecision"])
    return res['pricePrecision'], res['quantityPrecision']

# print(get_account_balance_v2(symbol="USDT"))
# pprint.pprint(get_exchange_info().symbols)
# print(get_exchange_info()["symbols"])
# print(get_pair_precisions("DOGEUSDT"))
