import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root)
sys.path.insert(0, root)

from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators,  add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades
from backtesting.macrossover.src.result import plot, summarize
import pandas as pd

data_path = "data/org/marketdata/BTCUSDT_15m_2000-11-21 00:00:00_2026-02-23 00:00:00.csv"

# load dataframe
rawdf= load_df(
    datapath=data_path, 
    start_date=pd.to_datetime("2025-10-01"),
    end_date=pd.to_datetime("2026-03-21")
)

# add technical indicsators
df_with_indicators = add_indicators(
    df = rawdf,
    short_window=10,
    long_window=20,
    trend_window=100,
    rsi_window=14
)

# define entry points for the trade
df_with_signals = add_signals(
    df = df_with_indicators,
    cross_persist=1,
    rsi_buy=55,
    rsi_sell=45
)

trades = simulate_trades(
    df=df_with_signals,
    tp_pct=0.05,
    sl_pct=0.02,
    max_candles=96 # keep open trade for max one day
)
resdf = evaluate_trades(
    trades=trades,
    init_portfolio=1000,
    trade_size_pct=0.1,
    fee_pct=0.005,
    leverage=10
)

summarize(resdf)
plot(df_with_signals)
