import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

def plot_portfolio_value(
    result: Dict,
    title: str = "Portfolio Value Over Time",
    figsize: tuple = (12, 6),
    show_benchmark: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot portfolio value over time with optional benchmark comparison.

    Args:
        result: Backtest result dictionary from ma_crossover_backtest
        title: Plot title
        figsize: Figure size
        show_benchmark: Whether to show buy-and-hold benchmark
        save_path: Optional path to save the figure

    Returns:
        matplotlib Figure object
    """
    # create figure
    fig, ax = plt.subplots(figsize=figsize)

    # plot strategy portfolio value
    ax.plot(result['timestamps'], result['portfolio_values'],
            label=f"{result['strategy']} (${result['initial_capital']:,.0f})",
            linewidth=2, color='blue')

    # plot benchmark (buy and hold)
    if show_benchmark:
        initial_btc_price = result['prices'].iloc[0]
        btc_holdings = result['initial_capital'] / initial_btc_price
        benchmark_values = btc_holdings * result['prices']
        ax.plot(result['timestamps'], benchmark_values,
                label="Buy & Hold BTC", linewidth=1.5, color='orange', alpha=0.7)

    # formatting
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Portfolio Value (USD)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_signals(
    result: Dict,
    start: Optional[str] = None,
    end: Optional[str] = None,
    figsize: tuple = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot price with buy/sell signals overlaid.

    Args:
        result: Backtest result dictionary from ma_crossover_backtest
        start: Optional start date filter, e.g. "2022-01-01"
        end: Optional end date filter, e.g. "2023-12-31"
        figsize: Figure size
        save_path: Optional path to save the figure

    Returns:
        matplotlib Figure object
    """
    timestamps = result["timestamps"].copy()
    trades = result["trades"].copy()

    def _filter(series):
        s = pd.Series(series.values, index=timestamps)
        if start:
            s = s[s.index >= pd.to_datetime(start)]
        if end:
            s = s[s.index <= pd.to_datetime(end)]
        return s

    price_series = _filter(result["prices"])
    ma_short = _filter(result["ma_short"])
    ma_long = _filter(result["ma_long"])
    ma_trend = _filter(result["ma_trend"])

    # filter trades to the same window
    buys = trades[trades["type"] == "buy"]
    sells = trades[trades["type"] == "sell"]
    if start:
        buys = buys[buys["timestamp"] >= pd.to_datetime(start)]
        sells = sells[sells["timestamp"] >= pd.to_datetime(start)]
    if end:
        buys = buys[buys["timestamp"] <= pd.to_datetime(end)]
        sells = sells[sells["timestamp"] <= pd.to_datetime(end)]

    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(price_series.index, price_series.values, color="gray", linewidth=1, label="Price", alpha=0.6)
    ax.plot(ma_short.index, ma_short.values, color="blue", linewidth=1, label="MA Short")
    ax.plot(ma_long.index, ma_long.values, color="orange", linewidth=1, label="MA Long")
    ax.plot(ma_trend.index, ma_trend.values, color="purple", linewidth=1, label="MA Trend", linestyle="--")

    ax.scatter(buys["timestamp"], buys["price"],
               marker="^", color="green", s=40, zorder=5, label="Buy")
    ax.scatter(sells["timestamp"], sells["price"],
               marker="v", color="red", s=40, zorder=5, label="Sell")

    ax.set_title(f"{result['strategy']} — Signals", fontsize=14, pad=20)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def save_trade_history(result: Dict, save_path: str) -> pd.DataFrame:
    """
    Save trade history from a backtest result to a CSV file.

    Args:
        result: Backtest result dictionary from ma_crossover_backtest
        save_path: Path to save the CSV file

    Returns:
        DataFrame of trades
    """
    trades = result["trades"]
    trades.to_csv(save_path, index=False)
    return trades