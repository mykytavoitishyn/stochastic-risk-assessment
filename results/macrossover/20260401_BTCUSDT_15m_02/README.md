# Grid Search — MA Crossover

**Run:** 2026-04-01
**Strategy:** MA Crossover
**Symbol:** BTCUSDT / 15m
**Train window:** 2024-03-21 → 2025-09-21
**Eval params:** {'init_portfolio': 1000, 'trade_size_pct': 0.1, 'fee_pct': 0.001, 'leverage': 1}

## Grid searched

| Param | Values |
|---|---|
| short_window | [10, 20, 50] |
| long_window | [50, 100, 200] |
| trend_window | [100, 200] |
| rsi_buy | [55] |
| rsi_sell | [45] |
| cross_persist | [2] |
| tp_pct | [0.03, 0.05, 0.08] |
| sl_pct | [0.01, 0.02, 0.03] |
| use_vol_filter | [False] |
| max_candles | [96, 192, 384] |

**Valid combos:** 189 | **Results:** 189

## Top 10 by Sharpe

|   short_window |   long_window |   trend_window |   tp_pct |   sl_pct | use_vol_filter   |   trades |   win_rate |   total_pnl |   sharpe |   max_drawdown |
|---------------:|--------------:|---------------:|---------:|---------:|:-----------------|---------:|-----------:|------------:|---------:|---------------:|
|             20 |           100 |            200 |     0.08 |     0.01 | False            |       57 |       38.6 |       11.84 |     0.69 |          -0.91 |
|             20 |           100 |            200 |     0.08 |     0.03 | False            |       56 |       42.9 |       11.95 |     0.65 |          -1.08 |
|             20 |           100 |            200 |     0.05 |     0.01 | False            |       57 |       38.6 |        8.04 |     0.51 |          -0.91 |
|             20 |           100 |            200 |     0.05 |     0.03 | False            |       56 |       42.9 |        8.15 |     0.48 |          -1.08 |
|             50 |           100 |            200 |     0.08 |     0.01 | False            |       72 |       30.6 |       10.78 |     0.46 |          -1.32 |
|             20 |           100 |            200 |     0.08 |     0.01 | False            |       53 |       26.4 |        9.74 |     0.43 |          -1.38 |
|             20 |           100 |            200 |     0.08 |     0.01 | False            |       56 |       28.6 |        8.9  |     0.4  |          -1.4  |
|             20 |           100 |            200 |     0.08 |     0.02 | False            |       56 |       42.9 |        6.75 |     0.36 |          -1.19 |
|             50 |           100 |            200 |     0.08 |     0.02 | False            |       71 |       40.8 |        7.29 |     0.28 |          -1.81 |
|             20 |           100 |            200 |     0.03 |     0.03 | False            |       56 |       44.6 |        4    |     0.27 |          -1.05 |
