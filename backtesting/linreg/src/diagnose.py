from backtesting.shared.diagnose import run_diagnose as _run
from backtesting.linreg.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf, lr_window=int(p["lr_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, slope_buy=p["slope_buy"], slope_sell=p["slope_sell"],
                       use_trend_filter=bool(p["use_trend_filter"]))

def _make_plot_kwargs(p):
    return {
        "price_overlays": [("ma_trend", "MA-trend", "orange")],
        "indicator_panel": {"col": "lr_slope_norm", "label": "LR Slope (norm)", "buy": p["slope_buy"], "sell": p["slope_sell"]},
    }

def run_diagnose(symbol, interval, test_start, test_end, eval_params, asset_type, run_dir=None, rank=0):
    return _run(
        strategy_name="Linear Regression Slope", runs_base="results/linreg",
        symbol=symbol, interval=interval,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df, make_plot_kwargs=_make_plot_kwargs,
        run_dir=run_dir, rank=rank,
    )
