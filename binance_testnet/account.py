import time
import hmac
import hashlib
from urllib.parse import urlencode

import requests


def ping_binance(base_url: str) -> bool:
    url = f"{base_url}/api/v3/ping"
    response = requests.get(url)
    return response.status_code == 200


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
