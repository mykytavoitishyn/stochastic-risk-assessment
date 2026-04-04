import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.shared.load import load_df
from backtesting.macrossover.src.ta import add_indicators, add_signals
from backtesting.shared.trade import simulate_trades, evaluate_trades
from backtesting.shared.result import plot, summarize
import pandas as pd

SYMBOL     = "BTCUSDT"
ASSET_TYPE = "crypto"
INTERVAL   = "15m"
RUN_START  = "2025-09-21"
RUN_END    = "2026-03-21"

INDICATORS = dict(short_window=10, long_window=50, trend_window=200, rsi_window=14)
SIGNALS    = dict(cross_persist=2, rsi_buy=55, rsi_sell=45, use_vol_filter=False)
TRADES     = dict(tp_pct=0.05, sl_pct=0.07, max_candles=None)
EVAL       = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=1)

df = load_df(ticker=SYMBOL, timeframe=INTERVAL, asset_type=ASSET_TYPE)
df = add_indicators(df, **INDICATORS)
df = add_signals(df, **SIGNALS)
df = df[(df["close_time"] > pd.to_datetime(RUN_START)) & (df["close_time"] <= pd.to_datetime(RUN_END))]

trades = simulate_trades(df, **TRADES)
resdf  = evaluate_trades(trades, **EVAL)

MA_OVERLAYS = [("ma_short", "MA-short", None), ("ma_long", "MA-long", None), ("ma_trend", "MA-trend", "orange")]

summarize(resdf)
plot(df, trades=resdf, price_overlays=MA_OVERLAYS)
