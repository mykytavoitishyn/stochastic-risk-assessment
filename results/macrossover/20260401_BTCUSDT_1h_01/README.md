# Grid Search — MA Crossover

**Run:** 2026-04-01
**Strategy:** MA Crossover
**Symbol:** BTCUSDT / 1h
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
|             20 |           100 |            200 |     0.08 |     0.01 | False            |       13 |       38.5 |       14.4  |     1.07 |          -0.35 |
|             20 |           100 |            200 |     0.03 |     0.01 | False            |       13 |       46.2 |        9.38 |     1.03 |          -0.35 |
|             20 |           100 |            200 |     0.05 |     0.01 | False            |       13 |       38.5 |        9.77 |     0.89 |          -0.35 |
|             10 |            50 |            200 |     0.03 |     0.01 | False            |       30 |       40   |       10.8  |     0.84 |          -0.74 |
|             10 |            50 |            200 |     0.05 |     0.01 | False            |       30 |       30   |       14.12 |     0.83 |          -0.74 |
|             20 |           100 |            200 |     0.08 |     0.02 | False            |       13 |       38.5 |       10.11 |     0.7  |          -0.37 |
|             10 |            50 |            200 |     0.08 |     0.01 | False            |       30 |       23.3 |       10.94 |     0.56 |          -1.03 |
|             20 |           100 |            200 |     0.08 |     0.03 | False            |       13 |       46.2 |        7.58 |     0.49 |          -0.45 |
|             20 |           100 |            200 |     0.03 |     0.02 | False            |       13 |       46.2 |        4.76 |     0.46 |          -0.37 |
|             20 |           100 |            200 |     0.05 |     0.02 | False            |       13 |       38.5 |        5.48 |     0.45 |          -0.37 |
