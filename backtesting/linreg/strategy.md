# Linear Regression Slope Strategy

## Overview

A trend-following strategy on BTC/USDT. Uses the slope of a rolling linear regression as the primary signal: positive slope indicates uptrend momentum, negative slope indicates downtrend. Slope is normalized by current price to be scale-invariant. Filtered by a long-term trend MA. Trades both long and short positions.

## Indicators

| Indicator | Description |
|-----------|-------------|
| `lr_slope` | `polyfit(arange, close[-lr_window:], 1)[0]` — raw slope of the best-fit line in price units per candle |
| `lr_slope_norm` | `lr_slope / close` — slope normalized by price (scale-invariant, ~0.001 = 0.1%/candle) |
| `ma_trend` | `close.rolling(trend_window).mean()` — long-term trend filter |
| `vol_ma` | `volume.rolling(vol_window).mean()` — optional volume filter |

## Entry Logic

| Signal | Condition |
|--------|-----------|
| Long (+1) | `lr_slope_norm` crosses above `slope_buy` AND `close > ma_trend` (if trend filter on) |
| Short (-1) | `lr_slope_norm` crosses below `slope_sell` AND `close < ma_trend` (if trend filter on) |
| Flat (0) | otherwise |

Crossover = current bar exceeds threshold AND previous bar did not.

## Exit Conditions (in priority order)

1. `tp` — Take-profit at target return %
2. `sl` — Stop-loss at loss threshold
3. `timeout` — Max holding period exceeded
4. `signal` — Opposite slope signal fires (flip position)
5. `end` — End of backtest data

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `lr_window` | Rolling regression window in candles | 30 |
| `trend_window` | Trend filter MA period | 200 |
| `vol_window` | Volume MA period | 20 |
| `slope_buy` | Normalized slope threshold to go long | 0.001 |
| `slope_sell` | Normalized slope threshold to go short | -0.001 |
| `use_trend_filter` | Enable long-term MA trend filter | True |
| `use_vol_filter` | Enable volume filter | False |
| `tp_pct` | Take-profit % | 0.05 |
| `sl_pct` | Stop-loss % | 0.03 |
| `max_candles` | Max holding period | 192 |

## Workflow

```
single_run.py    — quick test with fixed params
grid_search.py   — optimize params on train window → results/linreg/
validate.py      — OOS validate top configs from latest grid search
tune.py          — grid_search + validate in one shot
diagnose.py      — visualize best/rank-N config on test window
```
