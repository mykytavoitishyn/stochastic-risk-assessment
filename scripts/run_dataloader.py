import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root)
sys.path.insert(0, root)

from src.marketdata import get_klines, get_klines_df
import pandas as pd

BASE_URL = "https://api.binance.com"

# on binance there is no commodities data
SYMBOLS   = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
INTERVALS = ["15m", "30m", "1h", "4h"]

end_date   = pd.Timestamp.today().normalize()
start_date = end_date - pd.DateOffset(years=2)

for symbol in SYMBOLS:
    for interval in INTERVALS:
        path = f"data/org/marketdata/{symbol}_{interval}_{start_date.date()}_{end_date.date()}.csv"
        if os.path.exists(path):
            print(f"Skipping {symbol} {interval} (already exists)")
            continue
        print(f"Fetching {symbol} {interval} ...")
        start_int = int(start_date.value / 1e6)
        end_int   = int(end_date.value / 1e6)
        obj   = get_klines(BASE_URL, symbol=symbol, interval=interval, startTime=start_int, endTime=end_int)
        resdf = get_klines_df(obj)
        resdf.to_csv(path)
        print(f"  saved {len(resdf)} rows")