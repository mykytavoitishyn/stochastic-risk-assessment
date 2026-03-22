import requests
import pandas as pd
import time
import hmac
import hashlib
from urllib.parse import urlencode


def ping_binance(BASE_URL: str) -> bool:
    url = f"{BASE_URL}/api/v3/ping"
    response = requests.get(url)
    return response.status_code == 200


def send_market_buy_order(
    api_key: str,
    api_secret: str,
    symbol: str = "BTCUSDT",
    quantity: float = 0.0001,
    recv_window: int = 5000,
    base_url: str = "https://testnet.binance.vision",
):
    endpoint = "/api/v3/order"
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": quantity,
        "recvWindow": recv_window,
        "timestamp": int(time.time() * 1000),
    }
    query_string = urlencode(params)
    signature = hmac.new(api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.post(base_url + endpoint, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Order failed: {response.status_code} - {response.text}")
    return response.json()


def send_market_sell_order(
    api_key: str,
    api_secret: str,
    symbol: str = "BTCUSDT",
    quantity: float = 0.0001,
    recv_window: int = 5000,
    base_url: str = "https://testnet.binance.vision",
):
    endpoint = "/api/v3/order"
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity,
        "recvWindow": recv_window,
        "timestamp": int(time.time() * 1000),
    }
    query_string = urlencode(params)
    signature = hmac.new(api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.post(base_url + endpoint, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Order failed: {response.status_code} - {response.text}")
    return response.json()


def get_balance(
    api_key: str,
    api_secret: str,
    asset: str = "USDT",
    base_url: str = "https://testnet.binance.vision",
) -> dict:
    endpoint = "/api/v3/account"
    params = {
        "recvWindow": 5000,
        "timestamp": int(time.time() * 1000),
    }
    query_string = urlencode(params)
    signature = hmac.new(api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(base_url + endpoint, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to get balance: {response.status_code} - {response.text}")
    balances = response.json()["balances"]
    for b in balances:
        if b["asset"] == asset:
            return {"free": float(b["free"]), "locked": float(b["locked"])}
    return {"free": 0.0, "locked": 0.0}


def get_open_orders(
    api_key: str,
    api_secret: str,
    symbol: str = "BTCUSDT",
    base_url: str = "https://testnet.binance.vision",
) -> list:
    endpoint = "/api/v3/openOrders"
    params = {
        "symbol": symbol,
        "recvWindow": 5000,
        "timestamp": int(time.time() * 1000),
    }
    query_string = urlencode(params)
    signature = hmac.new(api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(base_url + endpoint, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to get open orders: {response.status_code} - {response.text}")
    return response.json()


def get_my_trades(
    api_key: str,
    api_secret: str,
    symbol: str = "BTCUSDT",
    limit: int = 50,
    base_url: str = "https://testnet.binance.vision",
) -> list:
    endpoint = "/api/v3/myTrades"
    params = {
        "symbol": symbol,
        "limit": limit,
        "recvWindow": 5000,
        "timestamp": int(time.time() * 1000),
    }
    query_string = urlencode(params)
    signature = hmac.new(api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(base_url + endpoint, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to get trades: {response.status_code} - {response.text}")
    return response.json()


def get_orderbook(BASE_URL: str, symbol: str , limit:int) -> object:
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


def get_klines(BASE_URL: str, symbol: str, interval: str, startTime: int = None, endTime: int = None):
    url = f"{BASE_URL}/api/v3/klines"
    all_klines = []
    
    interval_ms = {
        "1m":  1  * 60 * 1000,
        "5m":  5  * 60 * 1000,
        "15m": 15 * 60 * 1000,
        "30m": 30 * 60 * 1000,
        "1h":  60 * 60 * 1000,
        "4h":  4  * 60 * 60 * 1000,
        "1d":  24 * 60 * 60 * 1000,
    }
    
    if startTime is not None and endTime is not None and interval in interval_ms:
        time_diff_ms = endTime - startTime
        limit = int(time_diff_ms / interval_ms[interval]) + 1
    else:
        limit = 500
    
    if limit <= 1000:
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
    
    # for limit > 1000, paginate
    remaining = limit
    current_start = startTime
    
    while remaining > 0:
        batch_limit = min(1000, remaining)
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": batch_limit
        }
        if current_start:
            params["startTime"] = current_start
        if endTime:
            params["endTime"] = endTime
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            batch_data = response.json()
            if not batch_data:
                break
            
            all_klines.extend(batch_data)
            remaining -= len(batch_data)
            
            # update startTime for next batch
            if len(batch_data) == batch_limit and remaining > 0:
                last_close_time = batch_data[-1][6]
                current_start = last_close_time + 1
            else:
                break
        else:
            print("Error:", response.status_code)
            break
    
    return all_klines if all_klines else None
    
def get_klines_df(klines_raw: object):
    colnames = ["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"]

    df = pd.DataFrame(klines_raw, columns=colnames)

    df["open_time"] = pd.to_datetime(df["open_time"], unit = "ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit = "ms")

    numeric_cols = ["open_price", "high_price", "low_price", "close_price", "volume", "quote_asset_volume", "taker_buy_base_volume", "taker_buy_quote_volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df = df.drop(columns=["ignore"])
    
    return df