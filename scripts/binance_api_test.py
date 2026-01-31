from binance_api import ping_binance
from binance_api import get_klines
from binance_api import send_market_buy_order

import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

base_url = "https://testnet.binance.vision"


resp = ping_binance(base_url)
print(resp)


if ping_binance(base_url) == True:
    data = get_klines(base_url, "BTCUSDT", "5m", limit = 1000)
    colnames = ["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"]
    df = pd.DataFrame(data, columns=colnames)
    df["open_time"] = pd.to_datetime(df["open_time"], unit = "ms")
    df["open_time"] = pd.to_datetime(df["close_time"], unit = "ms")

    numeric_cols = ["open_price", "high_price", "low_price", "close_price", "volume", "quote_asset_volume", "taker_buy_base_volume", "taker_buy_quote_volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)




api_key = os.getenv("BINANCE_TESTNET_API_KEY")
api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")


try:
    result = send_market_buy_order(
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url  # Use testnet
    )
    print("\nOrder successful!")
    print(result)
except Exception as e:
    print(f"\nOrder failed: {e}")