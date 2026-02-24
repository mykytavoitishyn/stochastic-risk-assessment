import pandas as pd
import numpy as np

def ma_crossover_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    short_window: int = 20,
    long_window: int = 50,
    trend_window: int = 200
) -> dict:
    """
    MA Crossover strategy: buy on golden cross, sell on death cross.

    Parameters:
        df: DataFrame with "close_price" and "open_time" columns
        initial_capital: Starting capital in USDT
        short_window: Short MA period
        long_window: Long MA period
        trend_window: The longest MA period for trend following. 

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time").reset_index(drop=True)

    # two moving averages
    df["ma_short"] = df["close_price"].rolling(window=short_window).mean()
    df["ma_long"] = df["close_price"].rolling(window=long_window).mean()
    df["ma_trend"] = df["close_price"].rolling(window=trend_window).mean()

    # 1 -> buy
    # 0 -> no signal
    # -1 -> sell
    df["signal"] = 0
    df.loc[(df["ma_short"] > df["ma_long"]) & (df["ma_short"].shift(1) <= df["ma_long"].shift(1)), "signal"] = 1
    df.loc[(df["ma_short"] < df["ma_long"]) & (df["ma_short"].shift(1) >= df["ma_long"].shift(1)), "signal"] = -1

    # initialization
    cash = initial_capital
    btc_holdings = 0.0
    df["portfolio_value"] = 0.0
    trades = []
    entry_cash = None
    pct_per_trade= 0.05

    # we go all in
    start_idx = trend_window
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        price = row["close_price"]

        # and price > row["ma_trend"]
        if row["signal"] == 1 and cash > 0 :  # golden cross

            # entry buy
            entry_cash = cash * pct_per_trade
            buy_btc_holdings = entry_cash / price

            # update
            cash = cash - entry_cash
            btc_holdings = btc_holdings + buy_btc_holdings

            # log trade 
            trades.append({
                "type": "buy",
                "timestamp": row["open_time"],
                "price": price,
                "btc_amount": buy_btc_holdings,
                "pct_per_trade": pct_per_trade,
                "cash_in": entry_cash,
                "cash_out": None,
            })
        # and price < row["ma_trend"]
        elif row["signal"] == -1 and btc_holdings > 0:  # death cross

            # entry sell
            sell_btc_amount = btc_holdings * pct_per_trade
            cash_out = sell_btc_amount * price

            # update
            cash = cash + cash_out
            btc_holdings = btc_holdings - sell_btc_amount
            entry_cash = entry_cash - (entry_cash * pct_per_trade)

            trades.append({
                "type": "sell",
                "timestamp": row["open_time"],
                "price": price,
                "btc_amount": sell_btc_amount,
                "pct_per_trade": pct_per_trade,
                "cash_in": None,
                "cash_out": cash_out,
            })

        df.at[idx, "portfolio_value"] = cash + (btc_holdings * price) # current portfolio value

    df.loc[:start_idx, "portfolio_value"] = initial_capital

    return {
        "strategy": f"MA Crossover ({short_window}/{long_window})",
        "initial_capital": initial_capital,
        "portfolio_values": df["portfolio_value"],
        "prices": df["close_price"],
        "timestamps": df["open_time"],
        "trades": pd.DataFrame(trades),
        "ma_short": df["ma_short"],
        "ma_long": df["ma_long"],
        "ma_trend": df["ma_trend"],
    }
