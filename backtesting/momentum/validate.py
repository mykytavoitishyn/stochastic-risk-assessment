import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.momentum.src.validate import run_validation

SYMBOL   = "BTCUSDT"
INTERVAL = "15m"
DATA_START = "2024-03-21"
DATA_END   = "2026-03-21"
TEST_START = "2025-09-21"
TEST_END   = "2026-03-21"

EVAL_PARAMS = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=1)

run_validation(
    symbol=SYMBOL, interval=INTERVAL,
    data_start=DATA_START, data_end=DATA_END,
    test_start=TEST_START, test_end=TEST_END,
    eval_params=EVAL_PARAMS,
)
