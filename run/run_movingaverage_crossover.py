import pandas as pd
import matplotlib.pyplot as plt 

from backtesting.movingaverage_crossover import ma_crossover_backtest

from utils.evaluate import *


# hardcode data saving path
data_path = "data/org/marketdata/BTCUSDT_15m_2000-11-21 00:00:00_2026-02-23 00:00:00.csv"

df = pd.read_csv(data_path, index_col=0)
df['open_time'] = pd.to_datetime(df['open_time'])

print(f"Loaded {len(df)} days")
print(f"Date range: {df['open_time'].iloc[0].date()} to {df['open_time'].iloc[-1].date()}")

result = ma_crossover_backtest(df, initial_capital=1000, short_window=20, long_window=50, trend_window=200)

# save results

save_trade_history(result, save_path="results/trade_history.csv")
plot_portfolio_value(result, title="MA Crossover Performance", save_path=f"results/porfolio_over_time.png")
