from backtesting.shared.diagnose import run_diagnose as _run
from backtesting.momentum.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf, roc_window=int(p["roc_window"]), smooth_window=int(p["smooth_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, roc_buy=p["roc_buy"], roc_sell=p["roc_sell"])

def _make_plot_kwargs(p):
    return {
        "price_overlays": [("ma_trend", "MA-trend", "orange")],
        "indicator_panel": {"col": "roc_smooth", "label": "ROC (smoothed)", "buy": p["roc_buy"], "sell": p["roc_sell"]},
    }

def run_diagnose(symbol, interval, data_start, data_end, test_start, test_end, eval_params, run_dir=None, rank=0):
    return _run(
        runs_base="results/momentum",
        symbol=symbol, interval=interval,
        data_start=data_start, data_end=data_end,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params,
        build_df=_build_df, make_plot_kwargs=_make_plot_kwargs,
        run_dir=run_dir, rank=rank,
    )
