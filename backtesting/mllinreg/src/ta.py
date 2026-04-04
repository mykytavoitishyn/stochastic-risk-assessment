import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# --- compute features for the ML model ---
def add_indicators(df: pd.DataFrame, roc_short=5, roc_long=20, rsi_window=14,
                   ma_window=50, trend_window=200, vol_window=20) -> pd.DataFrame:
    # Momentum features
    df["roc_5"]  = df["close_price"].pct_change(roc_short)
    df["roc_20"] = df["close_price"].pct_change(roc_long)

    # RSI
    delta = df["close_price"].diff()
    gain = delta.clip(lower=0).rolling(rsi_window).mean()
    loss = (-delta.clip(upper=0)).rolling(rsi_window).mean()
    df["rsi"] = 100 - (100 / (1 + gain / loss))

    # Price relative to MA — captures mean reversion / trend strength
    df["ma_ratio"] = df["close_price"] / df["close_price"].rolling(ma_window).mean() - 1

    # Volume spike feature
    df["vol_ma"]    = df["quote_asset_volume"].rolling(vol_window).mean()
    df["vol_ratio"] = df["quote_asset_volume"] / df["vol_ma"] - 1

    # Long-term trend filter (used in add_signals)
    df["ma_trend"] = df["close_price"].rolling(trend_window).mean()

    return df.dropna()

_FEATURES = ["roc_5", "roc_20", "rsi", "ma_ratio", "vol_ratio"]

# --- walk-forward ML signal generation ---
def add_signals(df: pd.DataFrame, train_size=500, retrain_every=100,
                signal_threshold=0.001, use_trend_filter=True, use_vol_filter=False) -> pd.DataFrame:
    # Target: next candle return — known for all past rows, NaN for last row
    df["_next_return"] = df["close_price"].shift(-1) / df["close_price"] - 1
    df["_prediction"]  = 0.0
    df["signal"]       = 0

    model = LinearRegression()

    for i in range(train_size, len(df) - 1, retrain_every):
        train_slice = df.iloc[i - train_size:i].dropna(subset=_FEATURES + ["_next_return"])
        if len(train_slice) < 50:
            continue

        model.fit(train_slice[_FEATURES].values, train_slice["_next_return"].values)

        predict_end = min(i + retrain_every, len(df) - 1)
        pred_slice  = df.iloc[i:predict_end]
        valid       = pred_slice[_FEATURES].notna().all(axis=1)
        if valid.any():
            preds = model.predict(pred_slice.loc[valid, _FEATURES].values)
            df.loc[pred_slice.index[valid], "_prediction"] = preds

    pred = df["_prediction"]
    trend_ok_long  = (df["close_price"] > df["ma_trend"]) if use_trend_filter else True
    trend_ok_short = (df["close_price"] < df["ma_trend"]) if use_trend_filter else True
    vol_ok         = (df["quote_asset_volume"] > df["vol_ma"]) if use_vol_filter else True

    buy_mask = (
        (pred > signal_threshold)
        & (pred.shift(1) <= signal_threshold)
        & trend_ok_long
        & vol_ok
    )
    sell_mask = (
        (pred < -signal_threshold)
        & (pred.shift(1) >= -signal_threshold)
        & trend_ok_short
        & vol_ok
    )
    df.loc[buy_mask,  "signal"] = 1
    df.loc[sell_mask, "signal"] = -1

    df.drop(columns=["_next_return"], inplace=True)
    return df
