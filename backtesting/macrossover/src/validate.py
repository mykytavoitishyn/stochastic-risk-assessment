from backtesting.shared.validate import run_validation as _run
from backtesting.macrossover.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf, short_window=int(p["short_window"]), long_window=int(p["long_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, cross_persist=int(p["cross_persist"]), rsi_buy=p["rsi_buy"], rsi_sell=p["rsi_sell"], use_vol_filter=bool(p["use_vol_filter"]))

def _make_param_row(p):
    return {"short": int(p["short_window"]), "long": int(p["long_window"]), "trend": int(p["trend_window"]),
            "rsi_b": p["rsi_buy"], "rsi_s": p["rsi_sell"], "cp": int(p["cross_persist"]),
            "tp": p["tp_pct"], "sl": p["sl_pct"]}

def _format_best(b):
    return (f"short_window={int(b['short'])}, long_window={int(b['long'])}, trend_window={int(b['trend'])}\n"
            f"rsi_buy={b['rsi_b']}, rsi_sell={b['rsi_s']}, cross_persist={int(b['cp'])}\n"
            f"tp_pct={b['tp']}, sl_pct={b['sl']}")

def run_validation(symbol, interval, test_start, test_end, eval_params, asset_type, run_dir=None, top_n=10):
    return _run(
        strategy_name="MA Crossover", runs_base="results/macrossover",
        symbol=symbol, interval=interval,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df, make_param_row=_make_param_row, format_best=_format_best,
        run_dir=run_dir, top_n=top_n,
    )
