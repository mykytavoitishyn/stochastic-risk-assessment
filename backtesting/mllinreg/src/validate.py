from backtesting.shared.validate import run_validation as _run
from backtesting.mllinreg.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf)
    return add_signals(df, train_size=int(p["train_size"]), retrain_every=int(p["retrain_every"]),
                       signal_threshold=p["signal_threshold"], use_trend_filter=bool(p["use_trend_filter"]))

def _make_param_row(p):
    return {"train": int(p["train_size"]), "retrain": int(p["retrain_every"]),
            "thr": p["signal_threshold"], "trend_f": bool(p["use_trend_filter"]),
            "tp": p["tp_pct"], "sl": p["sl_pct"]}

def _format_best(b):
    return (f"train_size={int(b['train'])}, retrain_every={int(b['retrain'])}\n"
            f"signal_threshold={b['thr']}, use_trend_filter={b['trend_f']}\n"
            f"tp_pct={b['tp']}, sl_pct={b['sl']}")

def run_validation(symbol, interval, test_start, test_end, eval_params, asset_type, run_dir=None, top_n=10):
    return _run(
        strategy_name="ML Linear Regression", runs_base="results/mllinreg",
        symbol=symbol, interval=interval,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df, make_param_row=_make_param_row, format_best=_format_best,
        run_dir=run_dir, top_n=top_n,
    )
