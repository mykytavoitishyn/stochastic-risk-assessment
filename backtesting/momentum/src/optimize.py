from backtesting.shared.optimize import run_grid_search as _run
from backtesting.momentum.src.ta import add_indicators, add_signals

_COLS = ["roc_window", "smooth_window", "trend_window", "roc_buy", "roc_sell",
         "tp_pct", "sl_pct", "trades", "win_rate", "total_pnl", "sharpe", "max_drawdown"]

def _build_df(rawdf, p):
    df = add_indicators(rawdf, roc_window=int(p["roc_window"]), smooth_window=int(p["smooth_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, roc_buy=p["roc_buy"], roc_sell=p["roc_sell"])

def run_grid_search(symbol, interval, data_start, data_end, train_start, train_end, grid, eval_params):
    return _run(
        strategy_name="Momentum (Price ROC)", runs_base="results/momentum",
        symbol=symbol, interval=interval,
        data_start=data_start, data_end=data_end,
        train_start=train_start, train_end=train_end,
        grid=grid, eval_params=eval_params,
        build_df=_build_df,
        is_valid=lambda p: p["roc_buy"] > 0 and p["roc_sell"] < 0,
        readme_cols=_COLS,
    )
