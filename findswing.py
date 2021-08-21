import whpylib01 as wpl
import pprint

def find_swing(symbol="",interval="",type="H/L",start=-2,lookback=20):
# def find_swing(symbol="",interval="",type="H/L",start=-1,lookback=20):
    candles = wpl.get_candlesticks(symbol=symbol,interval=interval,limit=lookback)
    type = type.upper()
    for i in range(start,-lookback+1,-1):
        if type=="H":
            print(i,candles[i][2])
            if (candles[i][2]<candles[i-1][2]) and (candles[i-1][2]>candles[i-2][2]):
                s = candles[i-1][2]
                break
        elif type=="L":
            print(i,candles[i][3],candles[i-1][3],candles[i-2][3])
            if (candles[i][3]>candles[i-1][3]) and (candles[i-1][3]<candles[i-2][3]):
                s = candles[i-1][3]
                break
    # print(s)
    return({"index":int(i-1),"price":float(s)})

print(find_swing(symbol="DOGEUSDT",interval="15m",type="h",start=-2))
print(find_swing(symbol="DOGEUSDT",interval="15m",type="l",start=-4))
