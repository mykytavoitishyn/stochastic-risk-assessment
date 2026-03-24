import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root)
sys.path.insert(0, root)

from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators,  add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades
from backtesting.macrossover.src.result import plot, summarize
import pandas as pd

BACKTEST_START = "2026-03-01"
BACKTEST_END   = "2026-03-21"

# load dataframe
rawdf= load_df(
    ticker = "BTCUSDT",
    timeframe = "15m",
    start_date="2024-03-21",  # data file identifier — do not change
    end_date="2026-03-21"
)

# add technical indicsators
df_with_indicators = add_indicators(
    df = rawdf,
    short_window=10,
    long_window=50,
    trend_window=200,
    rsi_window=14
)

# define entry points for the trade
df_with_signals = add_signals(
    df = df_with_indicators,
    cross_persist=1,
    rsi_buy=55,
    rsi_sell=45
)

df_with_signals = df_with_signals[
    (df_with_signals["close_time"] > pd.to_datetime(BACKTEST_START)) &
    (df_with_signals["close_time"] <= pd.to_datetime(BACKTEST_END))
]

trades = simulate_trades(
    df=df_with_signals,
    tp_pct=0.03,
    sl_pct=0.01,
    max_candles=None # keep open trade for max one day
)
resdf = evaluate_trades(
    trades=trades,
    init_portfolio=1000,
    trade_size_pct=0.1,
    fee_pct=0.005,
    leverage=10
)

summarize(resdf)
plot(df_with_signals, trades=resdf)
