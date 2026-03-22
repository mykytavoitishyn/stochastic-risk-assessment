import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict
import matplotlib.dates as mdates

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

    sharpe       = trades.attrs.get("sharpe", "n/a")
    max_drawdown = trades.attrs.get("max_drawdown", "n/a")

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
        f"Sharpe ratio : {sharpe}",
        f"Max drawdown : {max_drawdown}%",
        "-" * 40,
        "Exit reasons :",
    ]
    for reason, count in trades["exit_reason"].value_counts().items():
        lines.append(f"  {reason:<10} {count:>4}  ({count/len(trades)*100:.1f}%)")
    lines.append("=" * 40)

    print("\n".join(lines))
