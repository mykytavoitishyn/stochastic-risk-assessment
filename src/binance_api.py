import requests

import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode


def ping_binance(BASE_URL):
    url = f"{BASE_URL}/api/v3/ping"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    else:
        return False
    
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
    


def send_market_buy_order(
    api_key: str,
    api_secret: str,
    symbol: str = "BTCUSDT",
    quantity: float = 0.0001,
    recv_window: int = 5000,
    base_url: str = "https://testnet.binance.vision"  # Default to testnet for safety
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
    signature = hmac.new(
        api_secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    params["signature"] = signature

    headers = {
        "X-MBX-APIKEY": api_key
    }

    response = requests.post(
        base_url + endpoint,
        headers=headers,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(f"Order failed: {response.status_code} - {response.text}")

    return response.json()

