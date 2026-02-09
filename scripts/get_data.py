from src.marketdata import get_klines, get_klines_df 
import pandas as pd

BASE_URL = "https://api.binance.com"

symbol = "BTCUSDT"
interval = "5m"

start_date = pd.to_datetime("2000-11-21")
end_date = pd.to_datetime("2025-11-21")

start_date_int = int(start_date.value / 1e6)
end_date_int = int(end_date.value / 1e6)

obj = get_klines(BASE_URL, symbol=symbol, interval=interval, startTime=start_date_int, endTime=end_date_int)

resdf = get_klines_df(obj)

resdf.to_csv(f"data/org/marketdata/{symbol}_{interval}_{start_date}_{end_date}.csv")