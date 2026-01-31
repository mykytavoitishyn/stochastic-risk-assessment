from scripts.marketdata import get_klines, get_klines_df 
import pandas as pd

BASE_URL = "https://api.binance.com"

symbol = "BTCUSDT"
interval = "5m"

start_date = int(pd.to_datetime("2000-11-21").value / 1e6)
end_date = int(pd.to_datetime("2025-11-21").value / 1e6)

print(start_date)
print(end_date)

obj = get_klines(BASE_URL, symbol=symbol, interval=interval, startTime=start_date, endTime=end_date)

resdf = get_klines_df(obj)

resdf.to_csv(f"data/org/marketdata/{symbol}_{interval}_{start_date}_{end_date}.csv")