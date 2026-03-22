import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Optional
import matplotlib.dates as mdates

def plot_portfolio_value(
    result: Dict,
    title: str = "Portfolio Value Over Time",
    figsize: tuple = (12, 6),
    show_benchmark: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """Plot portfolio value over time, optionally against a buy-and-hold BTC benchmark.

    Args:
        result: Dictionary containing simulation output with keys: "timestamps",
            "portfolio_values", "strategy", "initial_capital", and "prices".
        title: Chart title.
        figsize: Figure dimensions as (width, height) in inches.
        show_benchmark: If True, overlay a buy-and-hold BTC benchmark line.
        save_path: If provided, save the figure to this path at 300 DPI.

    Returns:
        The matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(result["timestamps"], result["portfolio_values"],
            label=f"{result["strategy"]} (${result["initial_capital"]:,.0f})",
            linewidth=2, color="blue")

    if show_benchmark:
        initial_btc_price = result["prices"].iloc[0]
        btc_holdings = result["initial_capital"] / initial_btc_price
        benchmark_values = btc_holdings * result["prices"]
        ax.plot(result["timestamps"], benchmark_values,
                label="Buy & Hold BTC", linewidth=1.5, color="orange", alpha=0.7)

    ax2 = ax.twinx()
    ax2.plot(result["timestamps"], result["prices"],
            color="gray", linewidth=1, alpha=0.4, label="BTC Price")

    trades = result["trades"]
    if not trades.empty:
        # support both column schemas
        side_col = "side" if "side" in trades.columns else "type"
        time_col = "time" if "time" in trades.columns else "timestamp"
        buy_val  = "BUY"  if side_col == "side" else "buy"
        sell_vals = ["SELL", "SELL (forced)"] if side_col == "side" else ["sell"]

        buys  = trades[trades[side_col] == buy_val]
        sells = trades[trades[side_col].isin(sell_vals)]
        ax2.scatter(buys[time_col],  buys["price"],  color="green", marker="^", s=60, zorder=5, label="Buy")
        ax2.scatter(sells[time_col], sells["price"], color="red",   marker="v", s=60, zorder=5, label="Sell")

    ax2.set_ylabel("BTC Price (USD)", fontsize=12)
        
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Portfolio Value (USD)", fontsize=12)
    ax.grid(True, alpha=0.3)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=10)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig



def save_trade_history(result: Dict, save_path: str) -> pd.DataFrame:
    """Save the trade history from a simulation result to a CSV file.

    Args:
        result: Dictionary containing simulation output with a "trades" key
            holding a DataFrame of executed trades.
        save_path: File path where the CSV will be written.

    Returns:
        The trades DataFrame.
    """
    trades = result["trades"]
    trades.to_csv(save_path, index=False)
    return trades


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


# --- print backtest summary ---
def summarize(trades: pd.DataFrame) -> None:
    if trades.empty:
        print("No trades.")
        return

    wins     = trades[trades["pnl"] > 0]
    losses   = trades[trades["pnl"] <= 0]
    win_rate = len(wins) / len(trades) * 100

    lines = [
        "=" * 40,
        f"Trades       : {len(trades)}",
        f"Win rate     : {win_rate:.1f}%  ({len(wins)}W / {len(losses)}L)",
        f"Total PnL    : ${trades['pnl'].sum():.2f}",
        f"Final portf. : ${trades['portfolio'].iloc[-1]:.2f}",
        f"Avg PnL/trade: ${trades['pnl'].mean():.2f}",
        f"Best trade   : ${trades['pnl'].max():.2f}",
        f"Worst trade  : ${trades['pnl'].min():.2f}",
        f"Avg candles  : {trades['candles'].mean():.1f}",
        "-" * 40,
        "Exit reasons :",
    ]
    for reason, count in trades["exit_reason"].value_counts().items():
        lines.append(f"  {reason:<10} {count:>4}  ({count/len(trades)*100:.1f}%)")
    lines.append("=" * 40)

    print("\n".join(lines))
