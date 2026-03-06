import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Optional

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