from src.binance.marketdata import get_klines, get_klines_df 
import pandas as pd

BASE_URL = "https://api.binance.com"

symbol = "BTCUSDT"
interval = "1d"
limit = 1000

obj = get_klines(BASE_URL, symbol=symbol, interval=interval, limit = limit)

resdf = get_klines_df(obj)

resdf.to_csv(f"data/org/marketdata/{symbol}_{interval}_{limit}.csv")