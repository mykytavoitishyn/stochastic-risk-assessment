import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

_console = Console()


# --- generic strategy plot ---
# price_overlays: list of (col_name, label, color) to plot on the price panel
# indicator_panel: optional dict {"col": str, "label": str, "buy": float, "sell": float}
#                  adds a middle panel with the indicator + threshold lines
def plot(
    df: pd.DataFrame,
    trades: pd.DataFrame = None,
    price_overlays: list = None,
    indicator_panel: dict = None,
) -> None:
    n_rows = 3 if indicator_panel else 2
    height_ratios = [3, 1.5, 1.5] if indicator_panel else [3, 1.5]
    fig, axes = plt.subplots(nrows=n_rows, ncols=1, figsize=(14, 4 * n_rows + 2),
                             sharex=True, gridspec_kw={"height_ratios": height_ratios})
    ax1 = axes[0]
    ax_ind = axes[1] if indicator_panel else None
    ax_port = axes[-1]

    # --- price ---
    ax1.plot(df["open_time"], df["close_price"], color="black", linewidth=0.8, label="Price")
    for col, label, color in (price_overlays or []):
        kw = {"alpha": 0.6, "linewidth": 0.8, "label": label}
        if color:
            kw["color"] = color
        ax1.plot(df["open_time"], df[col], **kw)

    EXIT_MARKERS = {"tp": ("*", 12), "sl": ("x", 8), "timeout": ("s", 6), "signal": ("o", 6), "end": ("D", 6)}
    EXIT_COLORS  = {"tp": "lime",    "sl": "red",    "timeout": "orange",  "signal": "grey",   "end": "purple"}

    if trades is not None and not trades.empty:
        for _, tr in trades.iterrows():
            side_color = "green" if tr["signal"] == 1 else "red"
            marker = "^" if tr["signal"] == 1 else "v"
            ax1.scatter(tr["entry_time"], tr["entry_price"], marker=marker, color=side_color, s=70, zorder=5)
            m, ms = EXIT_MARKERS.get(tr["exit_reason"], ("x", 8))
            ec = EXIT_COLORS.get(tr["exit_reason"], "grey")
            ax1.scatter(tr["exit_time"], tr["exit_price"], marker=m, color=ec, s=ms**2, zorder=5, linewidths=1.2)

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

    ax1.set_title("Price & Trades")
    ax1.grid(True, alpha=0.3)

    # --- optional indicator panel ---
    if indicator_panel and ax_ind is not None:
        col   = indicator_panel["col"]
        label = indicator_panel.get("label", col)
        buy   = indicator_panel.get("buy")
        sell  = indicator_panel.get("sell")

        ax_ind.plot(df["open_time"], df[col], color="steelblue", linewidth=0.9, label=label)
        ax_ind.axhline(0, color="grey", linewidth=0.6, linestyle="--")
        if buy is not None:
            ax_ind.axhline(buy,  color="green", linewidth=0.8, linestyle="--", label=f"Buy ({buy})")
        if sell is not None:
            ax_ind.axhline(sell, color="red",   linewidth=0.8, linestyle="--", label=f"Sell ({sell})")
        ax_ind.fill_between(df["open_time"], df[col], 0, where=(df[col] > 0), alpha=0.15, color="green")
        ax_ind.fill_between(df["open_time"], df[col], 0, where=(df[col] < 0), alpha=0.15, color="red")
        ax_ind.set_title(label)
        ax_ind.legend(fontsize=9)
        ax_ind.grid(True, alpha=0.3)

    # --- portfolio ---
    if trades is not None and not trades.empty:
        t_sorted = trades.sort_values("exit_time")
        init = t_sorted["portfolio"].iloc[0] - t_sorted["pnl"].iloc[0]
        ax_port.plot(t_sorted["exit_time"], t_sorted["portfolio"], color="steelblue", linewidth=1.2, label="Portfolio")
        ax_port.axhline(init, linestyle="--", color="grey", alpha=0.5, label="Initial")
        ax_port.fill_between(t_sorted["exit_time"], init, t_sorted["portfolio"], alpha=0.15, color="steelblue")
        ax_port.set_title("Portfolio Value Over Time")
        ax_port.legend(fontsize=9)
        ax_port.grid(True, alpha=0.3)
    else:
        ax_port.set_visible(False)

    date_fmt = mdates.DateFormatter("%b %d")
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=96))
    ax1.xaxis.set_major_formatter(date_fmt)

    plt.tight_layout()
    plt.show()


# --- print backtest summary ---
def summarize(trades: pd.DataFrame) -> None:
    if trades.empty:
        _console.print(Panel(Text("No trades.", style="dim"), title="Backtest Results", border_style="dim"))
        return

    wins     = trades[trades["pnl"] > 0]
    losses   = trades[trades["pnl"] <= 0]
    win_rate = len(wins) / len(trades) * 100

    sharpe          = trades.attrs.get("sharpe", "n/a")
    max_drawdown    = trades.attrs.get("max_drawdown", "n/a")
    final_portfolio = trades.attrs.get("final_portfolio", trades.sort_values("exit_time")["portfolio"].iloc[-1])
    total_pnl       = trades["pnl"].sum()

    # ── stats grid ───────────────────────────────────────────────────────────
    stats = Table.grid(padding=(0, 3))
    stats.add_column(style="bold cyan", no_wrap=True)
    stats.add_column(no_wrap=True)
    stats.add_column(style="bold cyan", no_wrap=True)
    stats.add_column(no_wrap=True)

    wr_style  = "green" if win_rate >= 50 else "red"
    pnl_style = "green" if total_pnl >= 0 else "red"
    dd_val    = max_drawdown if max_drawdown == "n/a" else f"{max_drawdown}%"

    stats.add_row(
        "Trades",      str(len(trades)),
        "Win rate",    Text(f"{win_rate:.1f}%  ({len(wins)}W / {len(losses)}L)", style=wr_style),
    )
    stats.add_row(
        "Total PnL",   Text(f"${total_pnl:+.2f}", style=pnl_style),
        "Final portf", f"${final_portfolio:.2f}",
    )
    stats.add_row(
        "Avg / trade", f"${trades['pnl'].mean():.2f}",
        "Sharpe",      str(sharpe),
    )
    stats.add_row(
        "Best trade",  Text(f"${trades['pnl'].max():.2f}", style="green"),
        "Drawdown",    Text(dd_val, style="red"),
    )
    stats.add_row(
        "Worst trade", Text(f"${trades['pnl'].min():.2f}", style="red"),
        "Avg candles", f"{trades['candles'].mean():.1f}",
    )

    # ── exit reasons ─────────────────────────────────────────────────────────
    reasons = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim", padding=(0, 2))
    reasons.add_column("Exit reason")
    reasons.add_column("Count", justify="right")
    reasons.add_column("Share", justify="right")

    REASON_STYLES = {"tp": "green", "sl": "red", "timeout": "yellow", "signal": "cyan", "end": "dim"}
    for reason, count in trades["exit_reason"].value_counts().items():
        style = REASON_STYLES.get(reason, "")
        reasons.add_row(
            Text(reason, style=style),
            str(count),
            f"{count / len(trades) * 100:.1f}%",
        )

    _console.print(Panel(
        Columns([stats, reasons], equal=False, expand=True),
        title="[bold]Backtest Results[/bold]",
        border_style="bright_blue",
        padding=(1, 2),
    ))
