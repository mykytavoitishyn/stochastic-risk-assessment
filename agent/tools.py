import time
from src.marketdata import get_klines, get_klines_df
from config import BINANCE_BASE_URL, DEFAULT_CANDLES, MA_PERIOD

TOOLS = [
    {
        "name": "market_snapshot",
        "description": (
            "Fetch the last N 15m BTC/USDT candles from Binance. "
            "Returns OHLCV, annualized volatility, and trend vs 200-candle MA."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "candles": {"type": "integer", "description": f"Number of 15m candles (default: {DEFAULT_CANDLES} = 24h)"},
            },
            "required": [],
        },
    }
]


def market_snapshot(inputs: dict) -> dict:
    candles = inputs.get("candles", DEFAULT_CANDLES)
    lookback = max(candles + MA_PERIOD, 300)
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - lookback * 15 * 60 * 1000

    raw = get_klines(BINANCE_BASE_URL, "BTCUSDT", "15m", startTime=start_ms, endTime=now_ms)
    if not raw:
        return {"error": "Failed to fetch data"}

    df = get_klines_df(raw)

    df = df.dropna()
    recent = df.tail(candles)

    returns = recent["close_price"].pct_change().dropna()
    price = float(df.iloc[-1]["close_price"])
    open_price = float(recent["close_price"].iloc[0])

    return {
        "open":        round(open_price, 2),
        "high":        round(float(recent["high_price"].max()), 2),
        "low":         round(float(recent["low_price"].min()), 2),
        "close":       round(price, 2),
        "change_pct":  round((price / open_price - 1) * 100, 2),
        "volume":      round(float(recent["quote_asset_volume"].sum()), 0),
        "period":      f"{candles} x 15m candles",
    }


TOOL_HANDLERS = {"market_snapshot": market_snapshot}
