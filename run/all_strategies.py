"""Run all strategies and compare their performance."""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from backtesting.buyandhold import buy_and_hold_backtest
from backtesting.dca import dca_backtest
from backtesting.rsi import rsi_backtest
from backtesting.macrossovers import ma_crossover_backtest
from backtesting.meanreversion import mean_reversion_backtest
from backtesting.volume import volume_backtest
from backtesting.grid import grid_trading_backtest
from backtesting.momentum import momentum_backtest
from backtesting.breakout import breakout_backtest
from src.metrics.performance import evaluate


def main():
    data_path = "data/org/marketdata/BTCUSDT_1d_974764800000_1763683200000.csv"

    print("Loading BTC daily data...")
    df = pd.read_csv(data_path, index_col=0)
    df['open_time'] = pd.to_datetime(df['open_time'])

    print(f"Loaded {len(df)} days")
    print(f"Date range: {df['open_time'].iloc[0].date()} to {df['open_time'].iloc[-1].date()}")

    strategies = [
        ("Buy & Hold", buy_and_hold_backtest(df)),
        ("DCA Weekly", dca_backtest(df, frequency='weekly')),
        ("RSI 14", rsi_backtest(df)),
        ("MA 50/200", ma_crossover_backtest(df)),
        ("Mean Reversion", mean_reversion_backtest(df)),
        ("Volume Spike", volume_backtest(df)),
        ("Grid Trading", grid_trading_backtest(df)),
        ("Momentum", momentum_backtest(df)),
        ("Breakout", breakout_backtest(df)),
    ]

    results = []
    for name, result in strategies:
        metrics = evaluate(result, periods_per_year=365)
        results.append({
            'Strategy': name,
            'Return %': f"{metrics['total_return_pct']:.1f}",
            'Sharpe': f"{metrics['sharpe_ratio']:.2f}",
            'Sortino': f"{metrics['sortino_ratio']:.2f}",
            'Max DD %': f"{metrics['max_drawdown_pct']:.1f}",
            'Win Rate %': f"{metrics['win_rate_pct']:.1f}",
        })

    print("\n" + "=" * 70)
    print("  STRATEGY COMPARISON")
    print("=" * 70)
    comparison_df = pd.DataFrame(results)
    print(comparison_df.to_string(index=False))
    print()


if __name__ == "__main__":
    main()
