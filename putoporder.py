import whpylib01
from datetime import datetime
import sys

PAIR = "DOGEUSDT"
TF = "15m"
op = 0.30274 #initial OP before SPARE
sl = 0.30008 #initial SL before SPARE
bs = 'B' if op>sl else 'S'
LOTS = 1
SPARE = whpylib01.AR(symbol=PAIR,interval=TF)/25
op += SPARE if bs=="B" else -SPARE
sl += -SPARE if bs=="B" else SPARE
print(op,sl)

RISK = 0.5 #in percent

blc = whpylib01.get_account_balance_v2(symbol="USDT")

riskDollar = RISK*blc/100
SPARE = whpylib01.AR(symbol=PAIR,interval=TF)/25

pricePrecision, quantityPrecision = whpylib01.get_pair_precisions(pair=PAIR)

rangeRisk = abs(op-sl)
positionSize = round(riskDollar/rangeRisk,quantityPrecision)
LOTS = positionSize

print(blc,riskDollar,SPARE,rangeRisk,positionSize)

# sys.exit(99)

print(datetime.now(),'start')
whpylib01.wh_send_order(symbol=PAIR,side="BUY" if bs=="B" else "SELL",type="OPEN",
                        price=op,quantity=LOTS)#,verbose=True)
print(datetime.now(),'sl sent')

with open('oporder.py',mode='w') as tf:
    tf.write('stopLoss='+str(sl)+'\n')
    tf.write('positionSize='+str(positionSize))
