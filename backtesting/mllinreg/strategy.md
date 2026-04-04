# ML Linear Regression Strategy

## Overview

A machine learning strategy on BTC/USDT. Uses sklearn `LinearRegression` to predict next-candle returns from a set of price/volume features. Signals are generated when the model's predicted return crosses a threshold. The model is retrained periodically using a **walk-forward** approach to avoid lookahead bias.

## Features

| Feature | Description |
|---------|-------------|
| `roc_5` | `close.pct_change(5)` — short-term momentum |
| `roc_20` | `close.pct_change(20)` — medium-term momentum |
| `rsi` | RSI(14) — overbought/oversold |
| `ma_ratio` | `close / MA(50) - 1` — price deviation from trend |
| `vol_ratio` | `volume / vol_MA(20) - 1` — volume spike |

## Target

`next_return = close[t+1] / close[t] - 1` — next candle's return. Known for all past rows; walk-forward ensures the model only ever trains on data prior to the prediction point.

## Walk-Forward Training

For each batch of `retrain_every` candles starting after `train_size` rows:
1. Train a fresh `LinearRegression` on the preceding `train_size` candles
2. Predict the next batch of `retrain_every` candles
3. Repeat, sliding forward

This prevents any future data from leaking into the model.

## Entry Logic

| Signal | Condition |
|--------|-----------|
| Long (+1) | `_prediction` crosses above `signal_threshold` AND `close > ma_trend` (if filter on) |
| Short (-1) | `_prediction` crosses below `-signal_threshold` AND `close < ma_trend` (if filter on) |
| Flat (0) | otherwise |

## Exit Conditions (in priority order)

1. `tp` — Take-profit at target return %
2. `sl` — Stop-loss at loss threshold
3. `timeout` — Max holding period exceeded
4. `signal` — Opposite prediction signal fires (flip position)
5. `end` — End of backtest data

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `train_size` | Number of candles used to train the model | 500 |
| `retrain_every` | Retrain the model every N candles | 100 |
| `signal_threshold` | Min predicted return magnitude to act | 0.001 |
| `use_trend_filter` | Enable long-term MA(200) trend filter | True |
| `use_vol_filter` | Enable volume filter | False |
| `tp_pct` | Take-profit % | 0.05 |
| `sl_pct` | Stop-loss % | 0.03 |
| `max_candles` | Max holding period | 192 |

## Workflow

```
single_run.py    — quick test with fixed params
grid_search.py   — optimize params on train window → results/mllinreg/
validate.py      — OOS validate top configs from latest grid search
tune.py          — grid_search + validate in one shot
diagnose.py      — visualize best/rank-N config on test window
```
