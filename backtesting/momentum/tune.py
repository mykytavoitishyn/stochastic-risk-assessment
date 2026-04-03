import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.momentum.src.optimize import run_grid_search
from backtesting.momentum.src.validate import run_validation

SYMBOL   = "BTCUSDT"
INTERVAL = "15m"
DATA_START  = "2024-03-21"
DATA_END    = "2026-03-21"
TRAIN_START = "2024-03-21"
TRAIN_END   = "2025-09-21"
TEST_START  = "2025-09-21"
TEST_END    = "2026-03-21"

EVAL_PARAMS = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=1)

GRID = {
    "roc_window":    [5, 10, 20],
    "smooth_window": [3],
    "trend_window":  [200],
    "roc_buy":       [2.0, 3.0],
    "roc_sell":      [-2.0, -3.0],
    "tp_pct":        [0.03, 0.05, 0.08],
    "sl_pct":        [0.02, 0.03],
    "max_candles":   [96, 192, 384],
}

run_dir = run_grid_search(
    symbol=SYMBOL, interval=INTERVAL,
    data_start=DATA_START, data_end=DATA_END,
    train_start=TRAIN_START, train_end=TRAIN_END,
    grid=GRID, eval_params=EVAL_PARAMS,
)

run_validation(
    symbol=SYMBOL, interval=INTERVAL,
    data_start=DATA_START, data_end=DATA_END,
    test_start=TEST_START, test_end=TEST_END,
    eval_params=EVAL_PARAMS,
    run_dir=run_dir,
)
