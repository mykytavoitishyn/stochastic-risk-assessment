import pandas as pd

# --- compute technical indicators ---
def add_indicators(df: pd.DataFrame, roc_window=10, smooth_window=3, trend_window=200, vol_window=20) -> pd.DataFrame:
    # Price Rate of Change (%)
    df["roc"] = df["close_price"].pct_change(roc_window) * 100
    # Smoothed ROC to reduce noise
    df["roc_smooth"] = df["roc"].rolling(smooth_window).mean()
    # Long-term trend filter
    df["ma_trend"] = df["close_price"].rolling(trend_window).mean()
    # Volume moving average
    df["vol_ma"] = df["quote_asset_volume"].rolling(vol_window).mean()

    return df.dropna()

# --- add buy/sell/hold signals based on ROC ---
def add_signals(df: pd.DataFrame, roc_buy=2.0, roc_sell=-2.0, use_vol_filter=False) -> pd.DataFrame:
    vol_ok = (df["quote_asset_volume"] > df["vol_ma"]) if use_vol_filter else True

    df["signal"] = 0
    buy_mask = (
        (df["roc_smooth"] > roc_buy)
        & (df["roc_smooth"].shift(1) <= roc_buy)
        & (df["close_price"] > df["ma_trend"])
        & vol_ok
    )
    sell_mask = (
        (df["roc_smooth"] < roc_sell)
        & (df["roc_smooth"].shift(1) >= roc_sell)
        & (df["close_price"] < df["ma_trend"])
        & vol_ok
    )
    df.loc[buy_mask, "signal"] = 1
    df.loc[sell_mask, "signal"] = -1
    return df
