import sys
import whpylib01 as wpl

PAIR = "DOGEUSDT"
PAIR = "ETHUSDT"
TF = "1d"
RISK = 0.5 #in percent of available balance
SIDE = "S"
SPARE = wpl.AR(symbol=PAIR,interval=TF)/25

#discretionary op & sl
op = ''#0.6
sl = ''#0.1

blc = wpl.get_account_balance_v2(symbol="USDT")
print("Curent balance=",blc)
riskDollar = RISK*blc/100
print("Risk$ =",riskDollar)

c = wpl.get_candlesticks(symbol=PAIR,interval=TF,limit=2)[-2]
op = op if op!='' else float(c[2] if SIDE=="B" else c[3]) + (SPARE if SIDE=="B" else -SPARE)
sl = sl if sl!='' else float(c[3] if SIDE=="B" else c[2]) + (-SPARE if SIDE=="B" else SPARE)

tp1 = op+(op-sl) if SIDE=="B" else op-(sl-op)
tp2 = op+(op-sl)*2 if SIDE=="B" else op-(sl-op)*2

pricePrecision, quantityPrecision = wpl.get_pair_precisions(pair="ETHUSDT")

rangeRisk = abs(op-sl)
print("Range risk=",rangeRisk)
positionSize = round(riskDollar/rangeRisk,quantityPrecision)
print("positionSize =",positionSize,quantityPrecision)
print("AR =",SPARE)

print(op,sl,tp1,tp2)
# sys.exit(99)

if SIDE=="B":
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="OPEN",price=op,quantity=positionSize)#,verbose=True) #open price
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=sl,quantity=positionSize)#,verbose=True) #SL
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=tp1,quantity=positionSize/3)#,verbose=True) #SL
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=tp2,quantity=positionSize/3)#,verbose=True) #SL
elif SIDE=="S":
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="OPEN",price=op,quantity=positionSize)#,verbose=True)
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=sl,quantity=positionSize)#,verbose=True)
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=tp1,quantity=positionSize/3)#,verbose=True) #SL
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=tp2,quantity=positionSize/3)#,verbose=True) #SL
