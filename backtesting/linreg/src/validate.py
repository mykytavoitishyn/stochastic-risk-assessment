from backtesting.shared.validate import run_validation as _run
from backtesting.linreg.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf, lr_window=int(p["lr_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, slope_buy=p["slope_buy"], slope_sell=p["slope_sell"],
                       use_trend_filter=bool(p["use_trend_filter"]))

def _make_param_row(p):
    return {"lr_w": int(p["lr_window"]), "trend": int(p["trend_window"]),
            "buy": p["slope_buy"], "sell": p["slope_sell"],
            "trend_f": bool(p["use_trend_filter"]), "tp": p["tp_pct"], "sl": p["sl_pct"]}

def _format_best(b):
    return (f"lr_window={int(b['lr_w'])}, trend_window={int(b['trend'])}\n"
            f"slope_buy={b['buy']}, slope_sell={b['sell']}, use_trend_filter={b['trend_f']}\n"
            f"tp_pct={b['tp']}, sl_pct={b['sl']}")

def run_validation(symbol, interval, test_start, test_end, eval_params, asset_type, run_dir=None, top_n=10):
    return _run(
        strategy_name="Linear Regression Slope", runs_base="results/linreg",
        symbol=symbol, interval=interval,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df, make_param_row=_make_param_row, format_best=_format_best,
        run_dir=run_dir, top_n=top_n,
    )
