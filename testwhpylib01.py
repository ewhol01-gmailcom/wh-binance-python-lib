import sys
import whpylib01 as wpl
from datetime import datetime

def showstarttime():
	print('\n'*3)
	print('-'*37,"Code Started",'-'*37)
	print(datetime.now()) 

def showendtime():
	print('-'*37,"Code ended",'-'*37)
	print(datetime.now())
	print('\n'*3)

PAIR = "DOGEUSDT"
# PAIR = "ETHUSDT"
TF = "15m"
RISK = 0.5 #in percent of available balance
SIDE = "b"
SPARE = wpl.AR(symbol=PAIR,interval=TF)/25

SIDE = SIDE.upper()

#discretionary op & sl
op = ''#0.6
sl = ''#0.1
sl = 0.30795

showstarttime()

blc = wpl.get_account_balance_v2(symbol="USDT")
riskDollar = RISK*blc/100

c = wpl.get_candlesticks(symbol=PAIR,interval=TF,limit=2)[-2]
op = op if op!='' else float(c[2] if SIDE=="B" else c[3])# + (SPARE if SIDE=="B" else -SPARE)
op += (SPARE if SIDE=="B" else -SPARE) #for some reasons, it works if do it this way
sl = sl if sl!='' else float(c[3] if SIDE=="B" else c[2])# + (-SPARE if SIDE=="B" else SPARE)
sl += (-SPARE if SIDE=="B" else SPARE)

tp1 = op+(op-sl) if SIDE=="B" else op-(sl-op)
tp2 = op+(op-sl)*2 if SIDE=="B" else op-(sl-op)*2
tp = op+(op-sl)*3 if SIDE=="B" else op-(sl-op)*3

pricePrecision, quantityPrecision = wpl.get_pair_precisions(pair=PAIR)

rangeRisk = abs(op-sl)
positionSize = round(riskDollar/rangeRisk,quantityPrecision)
showstarttime()
print("-"*91)
print("Balance=",blc,"Risk$ =",riskDollar,"Range=",rangeRisk,"Size =",positionSize,"@",quantityPrecision)
print(PAIR,SIDE,"@",op,"SL",sl,"TP1=",tp1,"TP2=",tp2)
print("SPARE =",SPARE)
print("-"*91)
showendtime()

sys.exit(99)

if SIDE=="B":
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="OPEN",price=op,quantity=positionSize)#,verbose=True) #open price
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=sl,quantity=positionSize)#,verbose=True) #SL
    # wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=tp1,quantity=positionSize/3)#,verbose=True) #SL
    # wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=tp2,quantity=positionSize/3)#,verbose=True) #SL
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=tp,quantity=positionSize)#,verbose=True) #SL
elif SIDE=="S":
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="OPEN",price=op,quantity=positionSize)#,verbose=True)
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=sl,quantity=positionSize)#,verbose=True)
    # wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=tp1,quantity=positionSize/3)#,verbose=True) #SL
    # wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=tp2,quantity=positionSize/3)#,verbose=True) #SL
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=tp,quantity=positionSize)#,verbose=True) #SL

showendtime()