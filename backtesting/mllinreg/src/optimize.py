from backtesting.shared.optimize import run_grid_search as _run
from backtesting.mllinreg.src.ta import add_indicators, add_signals

_COLS = ["train_size", "retrain_every", "signal_threshold", "use_trend_filter",
         "tp_pct", "sl_pct", "trades", "win_rate", "total_pnl", "sharpe", "max_drawdown"]

def _build_df(rawdf, p):
    df = add_indicators(rawdf)
    return add_signals(df, train_size=int(p["train_size"]), retrain_every=int(p["retrain_every"]),
                       signal_threshold=p["signal_threshold"], use_trend_filter=bool(p["use_trend_filter"]))

def run_grid_search(symbol, interval, train_start, train_end, grid, eval_params, asset_type):
    return _run(
        strategy_name="ML Linear Regression", runs_base="results/mllinreg",
        symbol=symbol, interval=interval,
        train_start=train_start, train_end=train_end,
        grid=grid, eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df,
        is_valid=lambda p: p["signal_threshold"] >= 0,
        readme_cols=_COLS,
        format_combo=lambda p: f"train={int(p['train_size'])} retrain={int(p['retrain_every'])} thr={p['signal_threshold']} tp={p['tp_pct']} sl={p['sl_pct']}",
    )
