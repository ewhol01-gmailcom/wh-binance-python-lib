import sys
import whpylib01 as wpl

PAIR = "DOGEUSDT"
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

rangeRisk = abs(op-sl)
positionSize = round(riskDollar/rangeRisk,wpl.quantityPrecision)
print("positionSize =",positionSize)

print(op,sl)
sys.exit(99)

if SIDE=="B":
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="OPEN",price=op,quantity=positionSize)#,verbose=True)
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="CLOSE",price=sl,quantity=positionSize)#,verbose=True)
elif SIDE=="S":
    wpl.wh_send_order(symbol=PAIR,side="SELL",type="OPEN",price=op,quantity=positionSize)#,verbose=True)
    wpl.wh_send_order(symbol=PAIR,side="BUY",type="CLOSE",price=sl,quantity=positionSize)#,verbose=True)
