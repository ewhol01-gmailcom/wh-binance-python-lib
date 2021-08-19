import whpylib01
from datetime import datetime
import sys

PAIR = "DOGEUSDT"
TF = "15m"

op = 0.30292 #already opened
sl = 0.30008 #to be ordered
bs = 'B' if op>sl else 'S'
LOTS = 33.0
# SPARE = whpylib01.AR(symbol=PAIR,interval=TF)/25
# sl += -SPARE if bs=="B" else SPARE #already adjusted if taken from the putoporder terminal output
import oporder
sl = oporder.stopLoss
LOTS = oporder.positionSize

RR = 3 #reward risk ratio
tp = op + (op-sl)*RR

print(bs,'op=',op,'sl=',sl,'tp=',tp,'op-sl=',op-sl,'('+str(round(abs(op-sl)*100/op,2))+'%)')

# sys.exit(99)

print(datetime.now(),'start')
whpylib01.wh_send_order(symbol=PAIR,side="BUY" if bs=="B" else "SELL",type="CLOSE",price=sl,quantity=LOTS)#,verbose=True)
print(datetime.now(),'sl sent')
whpylib01.wh_send_order(symbol=PAIR,side="BUY" if bs=="B" else "SELL",type="CLOSE",price=tp,quantity=LOTS,
                        workingType="CONTRACT_PRICE",)#,verbose=True) #for TP no need for MARK_PRICE
print(datetime.now(),'tp sent')
