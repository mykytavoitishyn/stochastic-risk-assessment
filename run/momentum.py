import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from backtesting.momentum import momentum_backtest
from src.metrics.performance import evaluate, print_evaluation


def main():
    data_path = "data/org/marketdata/BTCUSDT_1d_974764800000_1763683200000.csv"

    print("Loading BTC daily data...")
    df = pd.read_csv(data_path, index_col=0)
    df['open_time'] = pd.to_datetime(df['open_time'])

    print(f"Loaded {len(df)} days")
    print(f"Date range: {df['open_time'].iloc[0].date()} to {df['open_time'].iloc[-1].date()}")

    result = momentum_backtest(df, initial_capital=10000.0)
    metrics = evaluate(result, periods_per_year=365)
    print_evaluation(metrics)


if __name__ == "__main__":
    main()
