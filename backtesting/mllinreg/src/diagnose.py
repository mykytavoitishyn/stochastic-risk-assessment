from backtesting.shared.diagnose import run_diagnose as _run
from backtesting.mllinreg.src.ta import add_indicators, add_signals

def _build_df(rawdf, p):
    df = add_indicators(rawdf)
    return add_signals(df, train_size=int(p["train_size"]), retrain_every=int(p["retrain_every"]),
                       signal_threshold=p["signal_threshold"], use_trend_filter=bool(p["use_trend_filter"]))

def _make_plot_kwargs(p):
    return {
        "price_overlays": [("ma_trend", "MA-trend", "orange")],
        "indicator_panel": {"col": "_prediction", "label": "LR Prediction", "buy": p["signal_threshold"], "sell": -p["signal_threshold"]},
    }

def run_diagnose(symbol, interval, test_start, test_end, eval_params, asset_type, run_dir=None, rank=0):
    return _run(
        strategy_name="ML Linear Regression", runs_base="results/mllinreg",
        symbol=symbol, interval=interval,
        test_start=test_start, test_end=test_end,
        eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df, make_plot_kwargs=_make_plot_kwargs,
        run_dir=run_dir, rank=rank,
    )
