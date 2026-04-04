import requests
import pandas as pd


def get_ticker_24h(base_url: str, symbol: str) -> dict:
    url = f"{base_url}/api/v3/ticker/24hr"
    response = requests.get(url, params={"symbol": symbol})
    if response.status_code != 200:
        raise Exception(f"Failed to get 24h ticker: {response.status_code} - {response.text}")
    d = response.json()
    return {
        "price_change_pct": float(d["priceChangePercent"]),
        "volume":           float(d["quoteVolume"]),
        "high_24h":         float(d["highPrice"]),
        "low_24h":          float(d["lowPrice"]),
    }


def get_current_price(base_url: str, symbol: str) -> float:
    url = f"{base_url}/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": symbol})
    if response.status_code != 200:
        raise Exception(f"Failed to get price: {response.status_code} - {response.text}")
    return float(response.json()["price"])


def get_symbol_filters(base_url: str, symbol: str) -> dict:
    url = f"{base_url}/api/v3/exchangeInfo"
    response = requests.get(url, params={"symbol": symbol})
    if response.status_code != 200:
        raise Exception(f"Failed to get exchange info: {response.status_code} - {response.text}")
    symbols = response.json()["symbols"]
    info = next((s for s in symbols if s["symbol"] == symbol), None)
    if info is None:
        raise Exception(f"Symbol {symbol} not found")
    result = {}
    for f in info["filters"]:
        if f["filterType"] == "LOT_SIZE":
            result["min_qty"] = float(f["minQty"])
            result["max_qty"] = float(f["maxQty"])
            result["step_size"] = float(f["stepSize"])
        elif f["filterType"] == "MIN_NOTIONAL":
            result["min_notional"] = float(f["minNotional"])
    return result


def get_orderbook(base_url: str, symbol: str, limit: int) -> dict:
    url = f"{base_url}/api/v3/depth"
    params = {"symbol": symbol, "limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: ", response.status_code)


def get_recenttrades(base_url: str, symbol: str, limit: int):
    url = f"{base_url}/api/v3/trades"
    params = {"symbol": symbol, "limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: ", response.status_code)


def get_klines(base_url: str, symbol: str, interval: str, startTime: int = None, endTime: int = None):
    url = f"{base_url}/api/v3/klines"
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
        params = {"symbol": symbol, "interval": interval, "limit": limit}
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
        params = {"symbol": symbol, "interval": interval, "limit": batch_limit}
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
            if len(batch_data) == batch_limit and remaining > 0:
                last_close_time = batch_data[-1][6]
                current_start = last_close_time + 1
            else:
                break
        else:
            print("Error:", response.status_code)
            break

    return all_klines if all_klines else None


def get_klines_df(klines_raw):
    colnames = [
        "open_time", "open_price", "high_price", "low_price", "close_price",
        "volume", "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore",
    ]
    df = pd.DataFrame(klines_raw, columns=colnames)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    numeric_cols = [
        "open_price", "high_price", "low_price", "close_price", "volume",
        "quote_asset_volume", "taker_buy_base_volume", "taker_buy_quote_volume",
    ]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df = df.drop(columns=["ignore"])
    return df
