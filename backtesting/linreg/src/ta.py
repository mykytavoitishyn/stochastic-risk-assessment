import numpy as np
import pandas as pd

# --- compute technical indicators ---
def add_indicators(df: pd.DataFrame, lr_window=30, trend_window=200, vol_window=20) -> pd.DataFrame:
    # Rolling linear regression slope over lr_window candles
    def _slope(prices):
        x = np.arange(len(prices))
        return np.polyfit(x, prices, 1)[0]

    df["lr_slope"] = df["close_price"].rolling(lr_window).apply(_slope, raw=True)
    # Normalize slope by current price to make it scale-invariant (% per candle)
    df["lr_slope_norm"] = df["lr_slope"] / df["close_price"]
    # Long-term trend filter
    df["ma_trend"] = df["close_price"].rolling(trend_window).mean()
    # Volume moving average
    df["vol_ma"] = df["quote_asset_volume"].rolling(vol_window).mean()

    return df.dropna()

# --- add buy/sell/hold signals based on LR slope ---
def add_signals(df: pd.DataFrame, slope_buy=0.001, slope_sell=-0.001, use_trend_filter=True, use_vol_filter=False) -> pd.DataFrame:
    trend_ok_long  = (df["close_price"] > df["ma_trend"]) if use_trend_filter else True
    trend_ok_short = (df["close_price"] < df["ma_trend"]) if use_trend_filter else True
    vol_ok = (df["quote_asset_volume"] > df["vol_ma"]) if use_vol_filter else True

    df["signal"] = 0
    buy_mask = (
        (df["lr_slope_norm"] > slope_buy)
        & (df["lr_slope_norm"].shift(1) <= slope_buy)
        & trend_ok_long
        & vol_ok
    )
    sell_mask = (
        (df["lr_slope_norm"] < slope_sell)
        & (df["lr_slope_norm"].shift(1) >= slope_sell)
        & trend_ok_short
        & vol_ok
    )
    df.loc[buy_mask, "signal"] = 1
    df.loc[sell_mask, "signal"] = -1
    return df
