import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import numpy as np

os.chdir("/home/mykyta/Code/personal/stochastic-risk-assessment")


# --- load data ---
def load_df(datapath: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = pd.read_csv(datapath, index_col=0)
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df[(df["open_time"] >= start_date) & (df["open_time"] <= end_date)]
    return df

# --- compute technical indicator ---
def add_indicators(df: pd.DataFrame, short_window=20, long_window=50, trend_window=200, rsi_window=14) -> pd.DataFrame:
    df["ma_short"] = df["close_price"].rolling(short_window).mean()
    df["ma_long"] = df["close_price"].rolling(long_window).mean()
    df["ma_trend"] = df["close_price"].rolling(trend_window).mean()
    df["volume_change"] = df["quote_asset_volume"].pct_change()
    df["price_change"] = df["close_price"].pct_change()

    delta = df["close_price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.ewm(com=rsi_window - 1, min_periods=rsi_window).mean() / loss.ewm(com=rsi_window - 1, min_periods=rsi_window).mean()
    df["rsi"] = 100 - (100 / (1 + rs))

    return df.dropna()

# --- add buy/sell/hold signals based on indicators ---
def add_signals(df: pd.DataFrame, cross_persist=2, rsi_buy=55, rsi_sell=45) -> pd.DataFrame:
    df["cross_up"] = (df["ma_short"] > df["ma_long"]).astype(int)
    df["cross_down"] = (df["ma_short"] < df["ma_long"]).astype(int)

    df["signal"] = 0
    buy_mask = (
        (df["cross_up"].rolling(cross_persist).min() == 1)
        & (df["cross_up"].shift(cross_persist) == 0)
        & (df["close_price"] > df["ma_trend"])
        & (df["rsi"].shift(1) <= rsi_buy)   # not overbought at entry
    )
    sell_mask = (
        (df["cross_down"].rolling(cross_persist).min() == 1)
        & (df["cross_down"].shift(cross_persist) == 0)
        & (df["close_price"] < df["ma_trend"])
        & (df["rsi"].shift(1) >= rsi_sell)  # not oversold at entry
    )
    df.loc[buy_mask, "signal"] = 1
    df.loc[sell_mask, "signal"] = -1
    return df

# --- backtest the strategy ---
def simulate_trades(df: pd.DataFrame, init_portfolio=1_000, trade_size_pct=0.1, fee_pct=0.0005, leverage=10) -> pd.DataFrame:
    notional = init_portfolio * trade_size_pct * leverage
    signal_idx = df[df["signal"] != 0].index.tolist()
    trades = []

    position = 0
    entry_idx = None

    for idx in signal_idx:
        row = df.loc[idx]
        sig = row["signal"]

        if position == 0:
            position = sig
            entry_idx = idx
        elif sig == -position:
            entry_row = df.loc[entry_idx]
            entry = entry_row["close_price"]
            exit_price = row["close_price"]
            t_return = position * (exit_price - entry) / entry
            pnl = (t_return * notional) - notional * fee_pct * 2
            trades.append({
                "entry_time":  entry_row["open_time"],
                "exit_time":   row["open_time"],
                "entry_price": entry,
                "exit_price":  exit_price,
                "signal":      position,
                "return":      t_return,
                "pnl":         pnl,
                "candles":     len(df.loc[entry_idx:idx]) - 1,
            })
            position = 0
            entry_idx = None

    # force-exit any open position at end of data
    if position != 0:
        entry_row = df.loc[entry_idx]
        exit_row = df.iloc[-1]
        entry = entry_row["close_price"]
        exit_price = exit_row["close_price"]
        t_return = position * (exit_price - entry) / entry
        pnl = (t_return * notional) - notional * fee_pct * 2
        trades.append({
            "entry_time":  entry_row["open_time"],
            "exit_time":   exit_row["open_time"],
            "entry_price": entry,
            "exit_price":  exit_price,
            "signal":      position,
            "return":      t_return,
            "pnl":         pnl,
            "candles":     len(df.loc[entry_idx:]) - 1,
        })

    t = pd.DataFrame(trades)
    t["portfolio"] = init_portfolio + t["pnl"].cumsum()
    return t.sort_values(by="pnl")

# --- calculate the annualized sharpe ratio ---
def sharpe_ratio(trades: pd.DataFrame, risk_free_rate: float = 0.05) -> float:
    returns = trades["return"]
    if returns.std() == 0:
        return float("nan")
    years = (trades["exit_time"].max() - trades["entry_time"].min()).days / 365
    trades_per_year = len(trades) / years
    rf_per_trade = risk_free_rate / trades_per_year
    excess = returns - rf_per_trade
    return (excess.mean() / returns.std()) * (trades_per_year ** 0.5)

### --- print backetest results ---
def print_results(trades: pd.DataFrame, full: bool = False) -> None:
    if trades.empty:
        print("No trades.")
        return
    total_pnl = trades["pnl"].sum()
    win_rate = (trades["pnl"] > 0).mean()
    sharpe = sharpe_ratio(trades)
    print(f"Trades: {len(trades)} | Total PnL: ${total_pnl:.2f} | Win rate: {win_rate:.1%} | Final portfolio: ${trades['portfolio'].iloc[-1]:.2f} | Sharpe: {sharpe:.2f}")
    if full:
        print(trades[["entry_time", "exit_time", "entry_price", "exit_price", "signal", "return", "pnl", "candles"]].to_string(index=False))

### --- plot the strategy output ---
def plot(df: pd.DataFrame, trades: pd.DataFrame = None) -> None:
    _, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1, figsize=(12, 8))

    ax1.plot(df["open_time"], df["close_price"], label="BTC/USDT")
    ax1.plot(df["open_time"], df["ma_short"], alpha=0.7, label="MA-short")
    ax1.plot(df["open_time"], df["ma_long"], alpha=0.7, label="MA-long")
    ax1.plot(df["open_time"], df["ma_trend"], alpha=0.7, label="MA-trend")

    if trades is not None and not trades.empty:
        buy_entries  = trades.loc[trades["signal"] ==  1, "entry_time"]
        sell_entries = trades.loc[trades["signal"] == -1, "entry_time"]
    else:
        buy_entries  = df.loc[df["signal"] ==  1, "open_time"]
        sell_entries = df.loc[df["signal"] == -1, "open_time"]

    price_min, price_max = df["close_price"].min(), df["close_price"].max()
    ax1.vlines(buy_entries,  price_min, price_max, colors="green", alpha=0.5, label="Buy")
    ax1.vlines(sell_entries, price_min, price_max, colors="red",   alpha=0.5, label="Sell")
    ax1.set_title("MA's 20/50/200 BTC/USDT 15-min candle")
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    ax2.plot(df["open_time"], df["volume_change"], label="Volume change (%)")
    ax2.set_title("Quote asset volume change %")
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    ax3.plot(df["open_time"], df["price_change"], color="purple", label="Price change (%)")
    ax3.set_title("Close price change %")
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)

    ax4.plot(df["open_time"], df["rsi"], color="orange", label="RSI-14")
    ax4.axhline(60, linestyle="--", color="red", alpha=0.3, label="Overbought")
    ax4.axhline(40, linestyle="--", color="green", alpha=0.3, label="Oversold")
    ax4.set_title("RSI-14")
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)

    date_fmt = mdates.DateFormatter("%b %d")
    for ax in (ax1, ax2, ax3, ax4):
        ax.xaxis.set_major_formatter(date_fmt)

    plt.tight_layout()
    plt.show()

### --- run grid search algorithm to find the best hypoparameters ---
def run_grid_search(
        filepath: str = "data/org/marketdata/BTCUSDT_15m_2000-11-21 00:00:00_2026-02-23 00:00:00.csv",
        short_windows: list = [10, 20, 30],
        long_windows: list = [50, 70, 100],
        trend_windows: list = [100, 200],
        cross_persist: list = [1, 2, 3, 4],
        rsi_buy: int = 55,
        rsi_sell: int = 45,
        rsi_window: int = 14,
        trade_size_pcts: list = [0.02, 0.05, 0.1],
        fee_pct: float = 0.0005,
        leverage: int = 1,
        init_portfolio: int = 1000,
        start_date: str = "2026-01-01",
        end_date: str = "2026-03-01",
):
    all_results = []
    best_trades = None
    best_df = None
    best_portfolio = -float("inf")
    i = 0

    for short_window_i in short_windows:
        for long_window_i in long_windows:
            for trend_window_i in trend_windows:
                for cross_persist_i in cross_persist:
                    for trade_size_pct_i in trade_size_pcts:
                        df = load_df(filepath, start_date=start_date, end_date=end_date)
                        df = add_indicators(df, short_window=short_window_i, long_window=long_window_i, trend_window=trend_window_i, rsi_window=rsi_window)
                        df = add_signals(df, cross_persist=cross_persist_i, rsi_buy=rsi_buy, rsi_sell=rsi_sell)
                        trades = simulate_trades(df, init_portfolio=init_portfolio, trade_size_pct=trade_size_pct_i, fee_pct=fee_pct, leverage=leverage)

                        res_portfolio = init_portfolio + trades["pnl"].sum()
                        sharpe = sharpe_ratio(trades) if not trades.empty else float("nan")
                        result_entry = {
                            "short_window": short_window_i,
                            "long_window": long_window_i,
                            "trend_window": trend_window_i,
                            "cross_persist": cross_persist_i,
                            "trade_size_pct": trade_size_pct_i,
                            "final_portfolio": round(res_portfolio, 2),
                            "pct_return": round((res_portfolio * 100 / init_portfolio) - 100, 2),
                            "trade_count": len(trades),
                            "win_rate_pct": round(float((trades["pnl"] > 0).mean()) * 100, 1) if not trades.empty else 0,
                            "sharpe": round(float(sharpe), 3) if sharpe == sharpe else None,
                        }
                        all_results.append(result_entry)
                        i += 1
                        print(f"Combination {i}: portfolio={res_portfolio:.2f} ({result_entry['pct_return']:+.1f}%)")

                        if res_portfolio > best_portfolio:
                            best_portfolio = res_portfolio
                            best_trades = trades.copy()
                            best_df = df.copy()

    return best_trades, best_df, all_results


