from backtesting.shared.optimize import run_grid_search as _run
from backtesting.macrossover.src.ta import add_indicators, add_signals

_COLS = ["short_window", "long_window", "trend_window", "tp_pct", "sl_pct",
         "trades", "win_rate", "total_pnl", "sharpe", "max_drawdown"]

def _build_df(rawdf, p):
    df = add_indicators(rawdf, short_window=int(p["short_window"]), long_window=int(p["long_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, cross_persist=int(p["cross_persist"]), rsi_buy=p["rsi_buy"], rsi_sell=p["rsi_sell"], use_vol_filter=bool(p["use_vol_filter"]))

def run_grid_search(symbol, interval, data_start, data_end, train_start, train_end, grid, eval_params):
    return _run(
        strategy_name="MA Crossover", runs_base="results/macrossover",
        symbol=symbol, interval=interval,
        data_start=data_start, data_end=data_end,
        train_start=train_start, train_end=train_end,
        grid=grid, eval_params=eval_params,
        build_df=_build_df,
        is_valid=lambda p: p["short_window"] < p["long_window"] < p["trend_window"],
        readme_cols=_COLS,
    )
