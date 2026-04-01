# Grid Search — MA Crossover

**Run:** 2026-04-01
**Strategy:** MA Crossover
**Symbol:** BTCUSDT / 4h
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

**Valid combos:** 63 | **Results:** 63

## Top 10 by Sharpe

|   short_window |   long_window |   trend_window |   tp_pct |   sl_pct | use_vol_filter   |   trades |   win_rate |   total_pnl |   sharpe |   max_drawdown |
|---------------:|--------------:|---------------:|---------:|---------:|:-----------------|---------:|-----------:|------------:|---------:|---------------:|
|             20 |           100 |            200 |     0.03 |     0.03 | False            |        2 |      100   |        7.64 |     8.75 |           0    |
|             20 |           100 |            200 |     0.03 |     0.01 | False            |        2 |      100   |        7.64 |     8.75 |           0    |
|             20 |           100 |            200 |     0.03 |     0.02 | False            |        2 |      100   |        7.64 |     8.75 |           0    |
|             10 |            50 |            200 |     0.03 |     0.03 | False            |        8 |       75   |       16.52 |     1.54 |          -0.76 |
|             10 |            50 |            200 |     0.03 |     0.02 | False            |        8 |       62.5 |       12.88 |     1.22 |          -0.57 |
|             10 |           100 |            200 |     0.08 |     0.02 | False            |        4 |       50   |       14.09 |     1.04 |          -0.24 |
|             10 |            50 |            200 |     0.08 |     0.02 | False            |        8 |       50   |       15.86 |     0.99 |          -0.57 |
|             10 |            50 |            200 |     0.08 |     0.03 | False            |        8 |       62.5 |       15.83 |     0.93 |          -0.76 |
|             10 |            50 |            100 |     0.03 |     0.03 | False            |        9 |       66.7 |       11.62 |     0.9  |          -0.79 |
|             10 |            50 |            100 |     0.03 |     0.02 | False            |        9 |       55.6 |       10.14 |     0.88 |          -0.58 |
