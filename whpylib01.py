import hmac
import time
import hashlib
import requests
import json
from urllib.parse import urlencode

import sys
from pprint import pprint

import config
KEY = config.g_api_key
SECRET = config.g_secret_key

BASE_URL = 'https://fapi.binance.com' # production base url
# BASE_URL = 'https://testnet.binancefuture.com' # testnet base url

quantityPrecision = 0
pricePrecision = 0

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
    cp = get_current_price(symbol=symbol)
    if verbose:
        print(symbol,cp,side,type,price,quantity,"{:0.0{}f}".format(price,pricePrecision),"{:0.0{}f}".format(quantity,quantityPrecision))
    if side=="BUY":
        if type=="OPEN":
            if price<cp: #open buy below price
                r = _wh_send_order(symbol=symbol,side="BUY",positionSide="LONG",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order, buy below price
            elif price>cp: #open buy above price
                r = _wh_send_order(symbol=symbol,side="BUY",positionSide="LONG",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order, buy above price
        elif type=="CLOSE":
            if price<cp: #close buy below price
                r = _wh_send_order(symbol=symbol,side="BUY",positionSide="SHORT",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order close short below price            
            elif price>cp: #close buy above price
                r= _wh_send_order(symbol=symbol,side="BUY",positionSide="SHORT",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order close short above price    elif side=="SELL":
    elif side=="SELL":
        if type=="OPEN":
            if price<cp: #open sell below price
                r = _wh_send_order(symbol=symbol,side="SELL",positionSide="SHORT",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order, sell below price
            elif price>cp: #open sell above price
                r = _wh_send_order(symbol=symbol,side="SELL",positionSide="SHORT",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order, sell above price
        elif type=="CLOSE":
            if price<cp: #close sell below price
                r = _wh_send_order(symbol=symbol,side="SELL",positionSide="LONG",
                    type="STOP_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order close long below price
            elif price>cp: #close sell above price
                r = _wh_send_order(symbol=symbol,side="SELL",positionSide="LONG",
                    type="TAKE_PROFIT_MARKET",
                    quantity="{:0.0{}f}".format(quantity,quantityPrecision),
                    stopPrice="{:0.0{}f}".format(price,pricePrecision),
                    workingType=workingType,
                    verbose=verbose) #open order close long above price
    if verbose:
        print(r)
    return

def get_account_balance_v2(symbol="",simple=False,verbose=False):
    r = send_signed_request("GET","/fapi/v2/balance")
    if verbose:
        print(r)
    if symbol!="":
        for a in r:
            if a["asset"]==symbol:
                return(float(a["availableBalance"]))
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

def get_candlesticks(symbol="DOGEUSDT",interval="1d",limit=1,workingType="MARK_PRICE/CONTRACT_PRICE",verbose=False):
    if workingType=="MARK_PRICE/CONTRACT_PRICE":
        workingType="MARK_PRICE"
        req = "markPriceKlines"
    else:
        req = "klines"
    params = {
        "symbol" : symbol,
        "interval" : interval,
        "workingType" : workingType,
        "limit" : limit
    }
    r = send_signed_request("GET","/fapi/v1/"+req,params)
    if verbose:
        print(r)
    if limit==1:
        return(r[0])
    return(r)

def AR(symbol="DOGEUSDT",interval="1d",timeperiod=12,verbose=False): #average range
    candles = get_candlesticks(symbol=symbol, interval=interval, limit=timeperiod+1)
    s = 0
    for c in candles:
        s += float(c[2])-float(c[3])
    s -= float(candles[-1][2])-float(candles[-1][3])
    return(s/timeperiod)

def get_open_orders(symbol="DOGEUSDT", verbose=False):
    params = {
        "symbol" : symbol,
        "limit" : 5
    }
    r = send_signed_request("GET","/fapi/v1/openOrders",params,verbose)
    if verbose:
        print(r)
    return(r)

def get_order_byId(symbol='', orderId=0, verbose=False):
    params = {
        "symbol" : symbol,
        "orderId" : orderId
    }
    r = send_signed_request("GET","/fapi/v1/allOrders",params,verbose)
    if verbose:
        print(r)
    return(r[0])

def get_input(prompt='', default=''):
    p = prompt+'('
    p += default if type(default)=='str' else str(default)
    p += '):'
    gi = input(p)
    if gi=='':
        gi = default
        print(' ->',default,sep='')
    dt = type(default)
    gt = type(gi)
    if gt!=dt:
        ft = type(1.2)
        bt = type(True)
        if dt==ft:
            gi = float(gi)
        elif dt==bt:
            gi = gi.upper()
            gi = True if gi=='TRUE' else False
    return(gi)

# pprint(get_orders(symbol='DOGEUSDT',verbose=True))
# print(wh_send_order(symbol="DOGEUSDT",side="BUY",type="OPEN",price=0.7,quantity=1))
# print(get_order_byId(symbol='DOGEUSDT',orderId=9091772105)['symbol'])

# print(get_input(prompt='Symbol', default='DOGEUSDT'))
# print(get_input(prompt='Float', default=1.23))
# print(get_input('Pullback?',False))
