import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict
import matplotlib.dates as mdates


### --- plot the strategy output ---
def plot(df: pd.DataFrame, trades: pd.DataFrame = None) -> None:
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(14, 8), sharex=True)

    # --- price + MAs ---
    ax1.plot(df["open_time"], df["close_price"], color="black", linewidth=0.8, label="BTC/USDT")
    ax1.plot(df["open_time"], df["ma_short"],  alpha=0.7, linewidth=0.8, label="MA-short")
    ax1.plot(df["open_time"], df["ma_long"],   alpha=0.7, linewidth=0.8, label="MA-long")
    ax1.plot(df["open_time"], df["ma_trend"],  alpha=0.5, linewidth=0.8, label="MA-trend")

    EXIT_MARKERS = {"tp": ("*", 12), "sl": ("x", 8), "timeout": ("s", 6), "signal": ("o", 6), "end": ("D", 6)}
    EXIT_COLORS  = {"tp": "lime",    "sl": "red",    "timeout": "orange",  "signal": "grey",   "end": "purple"}

    if trades is not None and not trades.empty:
        for _, tr in trades.iterrows():
            side_color = "green" if tr["signal"] == 1 else "red"
            marker = "^" if tr["signal"] == 1 else "v"
            # entry
            ax1.scatter(tr["entry_time"], tr["entry_price"], marker=marker,
                        color=side_color, s=70, zorder=5)
            # exit — shape encodes reason, color encodes outcome
            m, ms = EXIT_MARKERS.get(tr["exit_reason"], ("x", 8))
            ec = EXIT_COLORS.get(tr["exit_reason"], "grey")
            ax1.scatter(tr["exit_time"], tr["exit_price"], marker=m,
                        color=ec, s=ms**2, zorder=5, linewidths=1.2)

        entry_long  = plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="green", markersize=9, label="Entry long")
        entry_short = plt.Line2D([0], [0], marker="v", color="w", markerfacecolor="red",   markersize=9, label="Entry short")
        exit_handles = [
            plt.Line2D([0], [0], marker=m, color="w", markerfacecolor=EXIT_COLORS[r],
                       markeredgecolor=EXIT_COLORS[r], markersize=8, label=f"Exit: {r}")
            for r, (m, _) in EXIT_MARKERS.items()
        ]
        ax1.legend(handles=[entry_long, entry_short, *exit_handles], fontsize=9)
    else:
        ax1.legend(fontsize=9)

    ax1.set_title("BTC/USDT — Price & Trades")
    ax1.grid(True, alpha=0.3)

    # --- portfolio over time ---
    if trades is not None and not trades.empty:
        t_sorted = trades.sort_values("exit_time")
        init = t_sorted["portfolio"].iloc[0] - t_sorted["pnl"].iloc[0]
        ax2.plot(t_sorted["exit_time"], t_sorted["portfolio"], color="steelblue", linewidth=1.2, label="Portfolio")
        ax2.axhline(init, linestyle="--", color="grey", alpha=0.5, label="Initial")
        ax2.fill_between(t_sorted["exit_time"], init, t_sorted["portfolio"], alpha=0.15, color="steelblue")
        ax2.set_title("Portfolio Value Over Time")
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
    else:
        ax2.set_visible(False)

    date_fmt = mdates.DateFormatter("%b %d")
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=96))
    ax1.xaxis.set_major_formatter(date_fmt)

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

    sharpe          = trades.attrs.get("sharpe", "n/a")
    max_drawdown    = trades.attrs.get("max_drawdown", "n/a")
    final_portfolio = trades.attrs.get("final_portfolio", trades.sort_values("exit_time")["portfolio"].iloc[-1])

    lines = [
        "=" * 40,
        f"Trades       : {len(trades)}",
        f"Win rate     : {win_rate:.1f}%  ({len(wins)}W / {len(losses)}L)",
        f"Total PnL    : ${trades['pnl'].sum():.2f}",
        f"Final portf. : ${final_portfolio:.2f}",
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
