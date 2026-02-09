import pandas as pd
from backtesting.dca import dca_backtest
from src.performance import evaluate, print_evaluation


def main():
    data_path = "data/org/marketdata/BTCUSDT_1d_974764800000_1763683200000.csv"

    print("Loading BTC daily data...")
    df = pd.read_csv(data_path, index_col=0)
    df['open_time'] = pd.to_datetime(df['open_time'])

    print(f"Loaded {len(df)} days")
    print(f"Date range: {df['open_time'].iloc[0].date()} to {df['open_time'].iloc[-1].date()}")

    result = dca_backtest(df, investment_amount=100.0, frequency='daily')
    metrics = evaluate(result, periods_per_year=365)
    print_evaluation(metrics)


if __name__ == "__main__":
    main()
