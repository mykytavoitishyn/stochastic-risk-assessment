import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.shared.load import load_df
from backtesting.mllinreg.src.ta import add_indicators, add_signals
from backtesting.shared.trade import simulate_trades, evaluate_trades
from backtesting.shared.result import plot, summarize
import pandas as pd

SYMBOL     = "BTCUSDT"
ASSET_TYPE = "crypto"
INTERVAL   = "15m"
RUN_START  = "2025-09-21"
RUN_END    = "2026-03-21"

INDICATORS = dict()   # fixed — no tunable indicator params
SIGNALS    = dict(train_size=500, retrain_every=100, signal_threshold=0.001, use_trend_filter=True)
TRADES     = dict(tp_pct=0.05, sl_pct=0.03, max_candles=192)
EVAL       = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=1)

df = load_df(ticker=SYMBOL, timeframe=INTERVAL, asset_type=ASSET_TYPE)
df = add_indicators(df, **INDICATORS)
df = add_signals(df, **SIGNALS)
df = df[(df["close_time"] > pd.to_datetime(RUN_START)) & (df["close_time"] <= pd.to_datetime(RUN_END))]

trades = simulate_trades(df, **TRADES)
resdf  = evaluate_trades(trades, **EVAL)

PRED_PANEL = {"col": "_prediction", "label": "LR Prediction",
              "buy": SIGNALS["signal_threshold"], "sell": -SIGNALS["signal_threshold"]}

summarize(resdf)
plot(df, trades=resdf, price_overlays=[("ma_trend", "MA-trend", "orange")], indicator_panel=PRED_PANEL)
