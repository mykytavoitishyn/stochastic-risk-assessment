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
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot strategy portfolio value
    ax.plot(result['timestamps'], result['portfolio_values'],
            label=f"{result['strategy']} (${result['initial_capital']:,.0f})",
            linewidth=2, color='blue')

    # Plot benchmark (buy and hold)
    if show_benchmark:
        initial_btc_price = result['prices'].iloc[0]
        btc_holdings = result['initial_capital'] / initial_btc_price
        benchmark_values = btc_holdings * result['prices']
        ax.plot(result['timestamps'], benchmark_values,
                label="Buy & Hold BTC", linewidth=1.5, color='orange', alpha=0.7)

    # Formatting
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Portfolio Value (USD)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig

def plot_rolling_metrics(
    result: Dict,
    window: int = 30,
    title: str = "Rolling Performance Metrics",
    figsize: tuple = (12, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot rolling performance metrics over time.

    Args:
        result: Backtest result dictionary
        window: Rolling window size in days
        title: Plot title
        figsize: Figure size
        save_path: Optional path to save the figure

    Returns:
        matplotlib Figure object
    """
    # Calculate rolling returns
    portfolio_returns = result['portfolio_values'].pct_change().dropna()
    rolling_returns = portfolio_returns.rolling(window=window).mean() * 100
    
    # Calculate rolling volatility
    rolling_volatility = portfolio_returns.rolling(window=window).std() * 100
    
    # Calculate rolling Sharpe ratio (assuming risk-free rate = 0)
    rolling_sharpe = rolling_returns / rolling_volatility
    
    # Create figure with three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, sharex=True)
    
    # Plot rolling returns
    ax1.plot(result['timestamps'][window:], rolling_returns[window:], 
             color='green', linewidth=2)
    ax1.set_title(f"{title}\n{window}-Day Rolling Metrics", fontsize=14, pad=20)
    ax1.set_ylabel("Rolling Return (%)", fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    
    # Plot rolling volatility
    ax2.plot(result['timestamps'][window:], rolling_volatility[window:], 
             color='red', linewidth=2)
    ax2.set_ylabel("Rolling Volatility (%)", fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Plot rolling Sharpe ratio
    ax3.plot(result['timestamps'][window:], rolling_sharpe[window:], 
             color='blue', linewidth=2)
    ax3.set_ylabel("Rolling Sharpe Ratio", fontsize=10)
    ax3.set_xlabel("Date", fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig

