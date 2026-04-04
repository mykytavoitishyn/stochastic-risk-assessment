from backtesting.shared.validate import run_validation as _run
from backtesting.momentum.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf, roc_window=int(p["roc_window"]), smooth_window=int(p["smooth_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, roc_buy=p["roc_buy"], roc_sell=p["roc_sell"])

def _make_param_row(p):
    return {"roc_w": int(p["roc_window"]), "smooth": int(p["smooth_window"]), "trend": int(p["trend_window"]),
            "roc_b": p["roc_buy"], "roc_s": p["roc_sell"], "tp": p["tp_pct"], "sl": p["sl_pct"]}

def _format_best(b):
    return (f"roc_window={int(b['roc_w'])}, smooth_window={int(b['smooth'])}, trend_window={int(b['trend'])}\n"
            f"roc_buy={b['roc_b']}, roc_sell={b['roc_s']}\n"
            f"tp_pct={b['tp']}, sl_pct={b['sl']}")

def run_validation(symbol, interval, test_start, test_end, eval_params, asset_type, run_dir=None, top_n=10):
    return _run(
        strategy_name="Momentum (Price ROC)", runs_base="results/momentum",
        symbol=symbol, interval=interval,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df, make_param_row=_make_param_row, format_best=_format_best,
        run_dir=run_dir, top_n=top_n,
    )
