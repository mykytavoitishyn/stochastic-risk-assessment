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
    
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(result['timestamps'], result['portfolio_values'],
            label=f"{result['strategy']} (${result['initial_capital']:,.0f})",
            linewidth=2, color='blue')

    if show_benchmark:
        initial_btc_price = result['prices'].iloc[0]
        btc_holdings = result['initial_capital'] / initial_btc_price
        benchmark_values = btc_holdings * result['prices']
        ax.plot(result['timestamps'], benchmark_values,
                label="Buy & Hold BTC", linewidth=1.5, color='orange', alpha=0.7)

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



def save_trade_history(result: Dict, save_path: str) -> pd.DataFrame:
    trades = result["trades"]
    trades.to_csv(save_path, index=False)
    return trades