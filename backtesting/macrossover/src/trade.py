import pandas as pd
import numpy as np

# --- replay signals and collect raw trade records ---
def simulate_trades(
    df: pd.DataFrame,
    tp_pct: float = None,       # take-profit threshold (e.g. 0.03 = 3%)
    sl_pct: float = None,       # stop-loss threshold  (e.g. 0.01 = 1%)
    max_candles: int = None,    # max holding period in candles
) -> pd.DataFrame:
    trades = []
    position = 0
    entry_idx = None
    entry_price = None
    candles_held = 0

    for idx in df.index:
        row = df.loc[idx]
        sig = row["signal"]

        if position == 0:
            if sig != 0:
                position = sig
                entry_idx = idx
                entry_price = row["close_price"]
                candles_held = 0
            continue

        price = row["close_price"]
        ret = position * (price - entry_price) / entry_price
        candles_held += 1

        exit_reason = None
        if tp_pct is not None and ret >= tp_pct:
            exit_reason = "tp"
        elif sl_pct is not None and ret <= -sl_pct:
            exit_reason = "sl"
        elif max_candles is not None and candles_held >= max_candles:
            exit_reason = "timeout"
        elif sig == -position:
            exit_reason = "signal"

        if exit_reason:
            entry_row = df.loc[entry_idx]
            trades.append({
                "entry_time":  entry_row["open_time"],
                "exit_time":   row["open_time"],
                "entry_price": entry_price,
                "exit_price":  price,
                "signal":      position,
                "candles":     candles_held,
                "exit_reason": exit_reason,
            })
            position = 0
            entry_idx = None
            entry_price = None
            candles_held = 0
            # if exit was triggered by an opposite signal, open the new position immediately
            if exit_reason == "signal":
                position = sig
                entry_idx = idx
                entry_price = price
                candles_held = 0

    # force-exit any open position at end of data
    if position != 0:
        entry_row = df.loc[entry_idx]
        exit_row = df.iloc[-1]
        trades.append({
            "entry_time":  entry_row["open_time"],
            "exit_time":   exit_row["open_time"],
            "entry_price": entry_price,
            "exit_price":  exit_row["close_price"],
            "signal":      position,
            "candles":     candles_held,
            "exit_reason": "end",
        })

    return pd.DataFrame(trades)


# --- compute returns, pnl, and portfolio curve ---
def evaluate_trades(trades: pd.DataFrame, init_portfolio=1_000, trade_size_pct=0.1, fee_pct=0.0005, leverage=10) -> pd.DataFrame:
    notional = init_portfolio * trade_size_pct * leverage
    t = trades.copy()
    t["return"] = t["signal"] * (t["exit_price"] - t["entry_price"]) / t["entry_price"]
    t["pnl"] = (t["return"] * notional) - notional * fee_pct * 2
    t["portfolio"] = init_portfolio + t["pnl"].cumsum()

    # max drawdown
    running_max = t["portfolio"].cummax()
    t["drawdown"] = (t["portfolio"] - running_max) / running_max

    # sharpe ratio (annualised, assuming each trade is independent)
    if t["pnl"].std() > 0:
        t.attrs["sharpe"] = round(t["pnl"].mean() / t["pnl"].std() * np.sqrt(len(t)), 2)
    else:
        t.attrs["sharpe"] = 0.0
    t.attrs["max_drawdown"] = round(t["drawdown"].min() * 100, 2)  # as %

    return t.sort_values(by="pnl")
