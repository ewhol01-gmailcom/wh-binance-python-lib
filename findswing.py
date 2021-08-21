import whpylib01 as wpl
import pprint

def find_swing(symbol="",interval="",start=-2,lookback=20):
    candles = wpl.get_candlesticks(symbol=symbol,interval=interval,limit=lookback)
    hi = 0 #hi index
    hp = 0 #hi price
    li = 0
    lp = 0
    for i in range(start,-lookback+1,-1):
        # print(i,'h =',candles[i][2],candles[i-1][2],candles[i-2][2])
        if (hi==0) and (candles[i][2]<candles[i-1][2]) and (candles[i-1][2]>candles[i-2][2]):
            s = candles[i-1][2]
            hp = float(s)
            hi = i-1
        # print(i,'l =',candles[i][3],candles[i-1][3],candles[i-2][3])
        if (li==0) and (candles[i][3]>candles[i-1][3]) and (candles[i-1][3]<candles[i-2][3]):
            s = candles[i-1][3]
            lp = float(s)
            li = i-1
        if hi!=0 and li!=0:
            break
    return({"hiIndex":hi, "hiPrice":hp, "loIndex":li, "loPrice":lp})

print(find_swing(symbol="DOGEUSDT",interval="15m",start=-2))
