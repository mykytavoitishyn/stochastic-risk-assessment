# MA Crossover Strategy

## Overview

Trend-following strategy on BTC/USDT using a dual moving average crossover for entry signals, filtered by a long-term trend MA and RSI momentum confirmation. Trades both long and short.

## Indicators

| Indicator | Purpose |
| --------- | ------- |
| MA-short (default 10) | Fast signal line |
| MA-long (default 50) | Slow signal line |
| MA-trend (default 200) | Trend filter — only trade in direction of trend |
| RSI-14 | Momentum filter — avoid entries in exhausted conditions |
| Volume MA | Optional volume filter — confirm signal with above-average volume |

## Entry Conditions

**Long** — all must be true:

- MA-short crosses above MA-long and stays above for `cross_persist` candles
- Close price is above MA-trend
- RSI on the previous candle is ≤ `rsi_buy` (not yet overbought)
- (If vol filter on) current volume > volume MA

**Short** — all must be true:

- MA-short crosses below MA-long and stays below for `cross_persist` candles
- Close price is below MA-trend
- RSI on the previous candle is ≥ `rsi_sell` (not yet oversold)
- (If vol filter on) current volume > volume MA

## Exit Conditions

Whichever triggers first:

| Reason | Condition |
| ------ | --------- |
| `tp` | Return ≥ `tp_pct` |
| `sl` | Return ≤ `-sl_pct` |
| `timeout` | Position held for `max_candles` candles |
| `signal` | Opposite crossover signal — close and flip |
| `end` | End of backtest data — force close |

## Position Sizing & Risk

- Trade size: `trade_size_pct × portfolio` (default 10%)
- Leverage: configurable (default 10×)
- Notional per trade: `portfolio × trade_size_pct × leverage`
- Fees: charged on entry and exit (`fee_pct × notional × 2`)
- Only one position open at a time

## Parameters (grid-searched)

| Parameter | Typical range |
| --------- | ------------- |
| `short_window` | 10 – 50 |
| `long_window` | 50 – 200 |
| `trend_window` | 100 – 200 |
| `cross_persist` | 1 – 2 candles |
| `rsi_buy` | 55 – 60 |
| `rsi_sell` | 40 – 45 |
| `tp_pct` | 3% – 8% |
| `sl_pct` | 1% – 3% |
