import numpy
import talib

import config
import pprint
import csv
from datetime import datetime

from binance_f import RequestClient
from binance_f.model import *
from binance_f.constant.test import *
from binance_f.base.printobject import *

SYMBOLS = ["DOGEUSDT","BTCUSDT","ETHUSDT",
			# "AXSUSDT",
			"ADAUSDT","XRPUSDT"]
TFLIST = ['3m','5m','15m','30m','1h','4h','1d']

def showstarttime():
	print('\n'*3)
	print('-'*37,"Code Started",'-'*37)
	print(datetime.now()) 

def showendtime():
	print('-'*37,"Code ended",'-'*37)
	print(datetime.now())
	print('\n'*3)

def extract(rawcandles, index=4): #0-4:time,O,H,L,C
	candles = []
	for c in rawcandles:
		# candles.append(float(c.close))
		if index==1:
			v = c.open
		elif index==2:
			v = c.high
		elif index==3:
			v = c.low
		elif index==4:
			v = c.close
		else:
			v = -1
		candles.append(float(v))
	return(numpy.array(candles))

showstarttime()

request_client = RequestClient(api_key=config.g_api_key, secret_key=config.g_secret_key)

# rawcandles = request_client.get_candlestick_data(symbol="DOGEUSDT", interval=CandlestickInterval.MIN15, 
# 												startTime=None, endTime=None, limit=16)

alldata = []
for s in SYMBOLS:
	for tf in TFLIST:
		# rawcandles = request_client.get_candlestick_data(symbol="DOGEUSDT", interval=tf, 
		# 												startTime=None, endTime=None, limit=16)
		# for EMA & RSI, lookback period should be higher to get more accurate result, 100 is close to Binance
		rawcandles = request_client.get_candlestick_data(symbol=s, interval=tf, 
														startTime=None, endTime=None, limit=100)
		closes = extract(rawcandles)
		highs = extract(rawcandles,2)
		lows = extract(rawcandles,3)
		ema13 = talib.EMA(closes,timeperiod=13)
		rsi5 = talib.RSI(closes,timeperiod=5)
		atr14 = talib.ATR(highs,lows,closes)
		a = [datetime.now(),s,tf]+ema13[-4:-1].tolist()+[ema13[-1]]+rsi5[-3:-1].tolist()+[rsi5[-1]]+[atr14[-1]] #+[eh13[-1]-el13[-1]]
		# eh13 = talib.EMA(highs,timeperiod=14)
		# el13 = talib.EMA(lows,timeperiod=14)
		# a = [datetime.now(),s,tf]+ema13[-4:-1].tolist()+[ema13[-1]]+rsi5[-3:-1].tolist()+[rsi5[-1]]+[atr14[-1]]+[eh13[-1]-el13[-1]]
		# a = [s,tf]+closes.tolist()+ema13.tolist()+rsi5.tolist()
		alldata.append(a)
pprint.pprint(alldata)

# write alldata to csv
with open('binance_symbols_data.csv','w',newline='') as f:
	cw = csv.writer(f)
	cw.writerow(['Time','Symbol','TF','EMA13(3)','EMA13(2)','EMA13(1)','EMA13(0)','RSI5(2)','RSI5(1)','RSI5(0)','ATR14'])
	for data in alldata:
		cw.writerow(data)

showendtime()