import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.mllinreg.src.optimize import run_grid_search
from backtesting.mllinreg.src.validate import run_validation

SYMBOL      = "BTCUSDT"
ASSET_TYPE  = "crypto"
INTERVAL    = "15m"
TRAIN_START = "2024-03-21"
TRAIN_END   = "2025-09-21"
TEST_START  = "2025-09-21"
TEST_END    = "2026-03-21"

EVAL_PARAMS = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=1)

GRID = {
    "train_size":        [300, 500],
    "retrain_every":     [50, 100],
    "signal_threshold":  [0.0, 0.0005, 0.001],
    "use_trend_filter":  [True, False],
    "tp_pct":            [0.03, 0.05, 0.08],
    "sl_pct":            [0.02, 0.03],
    "max_candles":       [96, 192, 384],
}

run_dir = run_grid_search(
    symbol=SYMBOL, interval=INTERVAL,
    train_start=TRAIN_START, train_end=TRAIN_END,
    grid=GRID, eval_params=EVAL_PARAMS, asset_type=ASSET_TYPE,
)

run_validation(
    symbol=SYMBOL, interval=INTERVAL,
    test_start=TEST_START, test_end=TEST_END,
    eval_params=EVAL_PARAMS, asset_type=ASSET_TYPE,
    run_dir=run_dir,
)
