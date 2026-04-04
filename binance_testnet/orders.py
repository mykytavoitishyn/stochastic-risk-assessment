import time
import hmac
import hashlib
from urllib.parse import urlencode

import requests


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
