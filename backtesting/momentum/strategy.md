# Momentum Strategy — Price ROC

## Overview

A pure price momentum strategy on BTC/USDT. Uses Rate of Change (ROC) as the primary signal, filtered by a long-term trend MA. Trades both long and short positions.

## Indicators

| Indicator | Description |
|-----------|-------------|
| `roc` | `(close - close[n]) / close[n] * 100` — raw % price change over `roc_window` candles |
| `roc_smooth` | `roc.rolling(smooth_window).mean()` — smoothed ROC to reduce noise |
| `ma_trend` | `close.rolling(trend_window).mean()` — long-term trend filter |
| `vol_ma` | `volume.rolling(20).mean()` — optional volume filter |

## Entry Logic

| Signal | Condition |
|--------|-----------|
| Long (+1) | `roc_smooth > roc_buy` AND `close > ma_trend` |
| Short (-1) | `roc_smooth < roc_sell` AND `close < ma_trend` |
| Flat (0) | otherwise |

## Exit Conditions (in priority order)

1. `tp` — Take-profit at target return %
2. `sl` — Stop-loss at loss threshold
3. `timeout` — Max holding period exceeded
4. `signal` — Opposite ROC signal fires (flip position)
5. `end` — End of backtest data

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `roc_window` | ROC lookback in candles | 10 |
| `smooth_window` | Rolling mean window for ROC | 3 |
| `trend_window` | Trend filter MA period | 200 |
| `roc_buy` | ROC threshold to go long (%) | 2.0 |
| `roc_sell` | ROC threshold to go short (%) | -2.0 |
| `tp_pct` | Take-profit % | 0.05 |
| `sl_pct` | Stop-loss % | 0.02 |
| `max_candles` | Max holding period | 192 |

## Workflow

```
single_run.py    — quick test with fixed params
grid_search.py   — optimize params on train window → results/momentum/
validate.py      — OOS validate top configs from latest grid search
tune.py          — grid_search + validate in one shot
diagnose.py      — visualize best/rank-N config on test window
```
