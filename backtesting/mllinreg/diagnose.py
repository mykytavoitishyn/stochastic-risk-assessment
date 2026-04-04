import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root); sys.path.insert(0, root)

from backtesting.mllinreg.src.diagnose import run_diagnose

SYMBOL     = "BTCUSDT"
ASSET_TYPE = "crypto"
INTERVAL   = "15m"
TEST_START = "2025-09-21"
TEST_END   = "2026-03-21"

EVAL_PARAMS = dict(init_portfolio=1000, trade_size_pct=0.1, fee_pct=0.001, leverage=1)

run_diagnose(
    symbol=SYMBOL, interval=INTERVAL,
    test_start=TEST_START, test_end=TEST_END,
    eval_params=EVAL_PARAMS, asset_type=ASSET_TYPE,
    rank=0,
)
