import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.shared.load import load_df
from backtesting.momentum.src.ta import add_indicators, add_signals
from backtesting.shared.trade import simulate_trades, evaluate_trades
from backtesting.shared.result import plot, summarize
import pandas as pd

SYMBOL    = "BTCUSDT"
INTERVAL  = "15m"
DATA_START = "2024-03-21"
DATA_END   = "2026-03-21"
RUN_START  = "2025-09-21"
RUN_END    = "2026-03-21"

INDICATORS = dict(roc_window=10, smooth_window=3, trend_window=200)
SIGNALS    = dict(roc_buy=2.0, roc_sell=-2.0)
TRADES     = dict(tp_pct=0.03, sl_pct=0.03, max_candles=192)
EVAL       = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=5)

df = load_df(ticker=SYMBOL, timeframe=INTERVAL, start_date=DATA_START, end_date=DATA_END)
df = add_indicators(df, **INDICATORS)
df = add_signals(df, **SIGNALS)
df = df[(df["close_time"] > pd.to_datetime(RUN_START)) & (df["close_time"] <= pd.to_datetime(RUN_END))]

trades = simulate_trades(df, **TRADES)
resdf  = evaluate_trades(trades, **EVAL)

ROC_PANEL = {"col": "roc_smooth", "label": "ROC (smoothed)", "buy": SIGNALS["roc_buy"], "sell": SIGNALS["roc_sell"]}

summarize(resdf)
plot(df, trades=resdf, price_overlays=[("ma_trend", "MA-trend", "orange")], indicator_panel=ROC_PANEL)
