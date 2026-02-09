import pandas as pd
import numpy as np


def calculate_returns(portfolio_values: pd.Series) -> pd.Series:
    """Calculate period-over-period returns."""
    return portfolio_values.pct_change().dropna()


def total_return(portfolio_values: pd.Series) -> float:
    """Total return as percentage."""
    return (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100


def total_return_multiple(portfolio_values: pd.Series) -> float:
    """Total return as multiple (e.g., 2.5x)."""
    return portfolio_values.iloc[-1] / portfolio_values.iloc[0]


def max_drawdown(portfolio_values: pd.Series) -> float:
    """Maximum drawdown as percentage (negative value)."""
    rolling_max = portfolio_values.expanding().max()
    drawdown = (portfolio_values - rolling_max) / rolling_max
    return drawdown.min() * 100


def annualized_return(portfolio_values: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized return percentage."""
    total_periods = len(portfolio_values)
    total_ret = portfolio_values.iloc[-1] / portfolio_values.iloc[0]
    years = total_periods / periods_per_year
    return (total_ret ** (1 / years) - 1) * 100


def annualized_volatility(portfolio_values: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized volatility (standard deviation of returns)."""
    returns = calculate_returns(portfolio_values)
    return returns.std() * np.sqrt(periods_per_year) * 100


def sharpe_ratio(portfolio_values: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Sharpe Ratio: (annualized return - risk free rate) / annualized volatility.

    Parameters:
        portfolio_values: Series of portfolio values
        risk_free_rate: Annual risk-free rate as decimal (e.g., 0.05 for 5%)
        periods_per_year: Trading periods per year (252 for daily, 365 for crypto)
    """
    ann_ret = annualized_return(portfolio_values, periods_per_year) / 100
    ann_vol = annualized_volatility(portfolio_values, periods_per_year) / 100

    if ann_vol == 0:
        return 0.0

    return (ann_ret - risk_free_rate) / ann_vol


def sortino_ratio(portfolio_values: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Sortino Ratio: uses only downside volatility.
    Better than Sharpe when returns are asymmetric.
    """
    returns = calculate_returns(portfolio_values)
    negative_returns = returns[returns < 0]

    ann_ret = annualized_return(portfolio_values, periods_per_year) / 100
    downside_vol = negative_returns.std() * np.sqrt(periods_per_year)

    if downside_vol == 0 or np.isnan(downside_vol):
        return 0.0

    return (ann_ret - risk_free_rate) / downside_vol


def calmar_ratio(portfolio_values: pd.Series, periods_per_year: int = 252) -> float:
    """Calmar Ratio: annualized return / max drawdown."""
    ann_ret = annualized_return(portfolio_values, periods_per_year)
    mdd = abs(max_drawdown(portfolio_values))

    if mdd == 0:
        return 0.0

    return ann_ret / mdd


def win_rate(returns: pd.Series) -> float:
    """Percentage of positive return periods."""
    if len(returns) == 0:
        return 0.0
    return (returns > 0).sum() / len(returns) * 100


def profit_factor(returns: pd.Series) -> float:
    """Gross profits / gross losses."""
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())

    if losses == 0:
        return float('inf') if gains > 0 else 0.0

    return gains / losses


def evaluate(backtest_result: dict, periods_per_year: int = 365) -> dict:
    """
    Evaluate a backtest result with all performance metrics.

    Parameters:
        backtest_result: dict from a strategy backtest (must have 'portfolio_values')
        periods_per_year: 252 for stocks, 365 for crypto daily data

    Returns:
        dict with all metrics
    """
    pv = backtest_result['portfolio_values']
    returns = calculate_returns(pv)

    metrics = {
        'strategy': backtest_result.get('strategy', 'Unknown'),
        'initial_capital': backtest_result.get('initial_capital', pv.iloc[0]),
        'final_value': pv.iloc[-1],
        'total_return_pct': total_return(pv),
        'total_return_multiple': total_return_multiple(pv),
        'annualized_return_pct': annualized_return(pv, periods_per_year),
        'annualized_volatility_pct': annualized_volatility(pv, periods_per_year),
        'sharpe_ratio': sharpe_ratio(pv, periods_per_year=periods_per_year),
        'sortino_ratio': sortino_ratio(pv, periods_per_year=periods_per_year),
        'calmar_ratio': calmar_ratio(pv, periods_per_year),
        'max_drawdown_pct': max_drawdown(pv),
        'win_rate_pct': win_rate(returns),
        'profit_factor': profit_factor(returns),
        'num_periods': len(pv),
    }

    return metrics


def print_evaluation(metrics: dict) -> None:
    """Pretty print evaluation metrics."""
    print(f"\n{'='*50}")
    print(f"  {metrics['strategy']} - Performance Report")
    print(f"{'='*50}")

    print(f"\nReturns:")
    print(f"  Initial Capital:    ${metrics['initial_capital']:,.2f}")
    print(f"  Final Value:        ${metrics['final_value']:,.2f}")
    print(f"  Total Return:       {metrics['total_return_pct']:.2f}% ({metrics['total_return_multiple']:.2f}x)")
    print(f"  Annualized Return:  {metrics['annualized_return_pct']:.2f}%")

    print(f"\nRisk Metrics:")
    print(f"  Volatility (ann.):  {metrics['annualized_volatility_pct']:.2f}%")
    print(f"  Max Drawdown:       {metrics['max_drawdown_pct']:.2f}%")

    print(f"\nRisk-Adjusted:")
    print(f"  Sharpe Ratio:       {metrics['sharpe_ratio']:.3f}")
    print(f"  Sortino Ratio:      {metrics['sortino_ratio']:.3f}")
    print(f"  Calmar Ratio:       {metrics['calmar_ratio']:.3f}")

    print(f"\nTrading Stats:")
    print(f"  Win Rate:           {metrics['win_rate_pct']:.1f}%")
    print(f"  Profit Factor:      {metrics['profit_factor']:.2f}")
    print(f"  Periods:            {metrics['num_periods']}")
    print()
