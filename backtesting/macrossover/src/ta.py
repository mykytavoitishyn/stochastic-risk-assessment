import pandas as pd

# --- compute technical indicator ---
def add_indicators(df: pd.DataFrame, short_window=20, long_window=50, trend_window=200, rsi_window=14, vol_window=20) -> pd.DataFrame:
    df["ma_short"] = df["close_price"].rolling(short_window).mean()
    df["ma_long"] = df["close_price"].rolling(long_window).mean()
    df["ma_trend"] = df["close_price"].rolling(trend_window).mean()
    df["volume_change"] = df["quote_asset_volume"].pct_change()
    df["price_change"] = df["close_price"].pct_change()
    df["vol_ma"] = df["quote_asset_volume"].rolling(vol_window).mean()

    delta = df["close_price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.ewm(com=rsi_window - 1, min_periods=rsi_window).mean() / loss.ewm(com=rsi_window - 1, min_periods=rsi_window).mean()
    df["rsi"] = 100 - (100 / (1 + rs))

    return df.dropna()

# --- add buy/sell/hold signals based on indicators ---
def add_signals(df: pd.DataFrame, cross_persist=2, rsi_buy=55, rsi_sell=45, use_vol_filter=True) -> pd.DataFrame:
    df["cross_up"] = (df["ma_short"] > df["ma_long"]).astype(int)
    df["cross_down"] = (df["ma_short"] < df["ma_long"]).astype(int)

    vol_ok = (df["quote_asset_volume"] > df["vol_ma"]) if use_vol_filter else True

    df["signal"] = 0
    buy_mask = (
        (df["cross_up"].rolling(cross_persist).min() == 1)
        & (df["cross_up"].shift(cross_persist) == 0)
        & (df["close_price"] > df["ma_trend"])
        & (df["rsi"].shift(1) <= rsi_buy)
        & vol_ok
    )
    sell_mask = (
        (df["cross_down"].rolling(cross_persist).min() == 1)
        & (df["cross_down"].shift(cross_persist) == 0)
        & (df["close_price"] < df["ma_trend"])
        & (df["rsi"].shift(1) >= rsi_sell)
        & vol_ok
    )
    df.loc[buy_mask, "signal"] = 1
    df.loc[sell_mask, "signal"] = -1
    return df