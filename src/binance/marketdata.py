import requests
import pandas as pd

def get_orderbook(BASE_URL, symbol, limit):
    url = f"{BASE_URL}/api/v3/depth"
    params = {"symbol": symbol, "limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: ", response.status_code)


def get_recenttrades(BASE_URL: str, symbol: str, limit: int):
    url = f"{BASE_URL}/api/v3/trades"
    params = {"symbol": symbol, "limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: ", response.status_code)


def get_klines(BASE_URL: str, symbol: str, interval: str, limit: int = 500, startTime: int = None, endTime: int = None):
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    if startTime:
        params["startTime"] = startTime
    if endTime:
        params["endTime"] = endTime

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None
    
def get_klines_df(klines_raw: object):
    colnames = ["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"]

    df = pd.DataFrame(klines_raw, columns=colnames)

    df["open_time"] = pd.to_datetime(df["open_time"], unit = "ms")
    df["open_time"] = pd.to_datetime(df["close_time"], unit = "ms")

    numeric_cols = ["open_price", "high_price", "low_price", "close_price", "volume", "quote_asset_volume", "taker_buy_base_volume", "taker_buy_quote_volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df = df.drop(columns=["ignore"])
    
    return df
