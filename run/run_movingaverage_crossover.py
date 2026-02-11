import pandas as pd
import matplotlib.pyplot as plt 

from backtesting.movingaverage_crossover import ma_crossover_backtest

from utils.evaluate import *


data_path = "data/org/marketdata/BTCUSDT_5m_2000-11-21 00:00:00_2025-11-21 00:00:00.csv"

print("Loading BTC daily data...")
df = pd.read_csv(data_path, index_col=0)
df['open_time'] = pd.to_datetime(df['open_time'])

print(f"Loaded {len(df)} days")
print(f"Date range: {df['open_time'].iloc[0].date()} to {df['open_time'].iloc[-1].date()}")

result = ma_crossover_backtest(df, initial_capital=2500, short_window=50, long_window=200)

# Generate all visualizations
plot_portfolio_value(result, title="MA Crossover Performance", save_path="results/porfolio_over_time.png")

