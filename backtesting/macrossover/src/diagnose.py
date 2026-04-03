from backtesting.shared.diagnose import run_diagnose as _run
from backtesting.macrossover.src.ta import add_indicators, add_signals

_OVERLAYS = [("ma_short", "MA-short", None), ("ma_long", "MA-long", None), ("ma_trend", "MA-trend", "orange")]

def _build_df(rawdf, p):
    df = add_indicators(rawdf, short_window=int(p["short_window"]), long_window=int(p["long_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, cross_persist=int(p["cross_persist"]), rsi_buy=p["rsi_buy"], rsi_sell=p["rsi_sell"], use_vol_filter=bool(p["use_vol_filter"]))

def run_diagnose(symbol, interval, data_start, data_end, test_start, test_end, eval_params, run_dir=None, rank=0):
    return _run(
        runs_base="results/macrossover",
        symbol=symbol, interval=interval,
        data_start=data_start, data_end=data_end,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params,
        build_df=_build_df,
        make_plot_kwargs=lambda p: {"price_overlays": _OVERLAYS},
        run_dir=run_dir, rank=rank,
    )
