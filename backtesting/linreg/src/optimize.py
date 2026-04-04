from backtesting.shared.optimize import run_grid_search as _run
from backtesting.linreg.src.ta import add_indicators, add_signals

_COLS = ["lr_window", "slope_buy", "slope_sell", "use_trend_filter",
         "tp_pct", "sl_pct", "trades", "win_rate", "total_pnl", "sharpe", "max_drawdown"]

def _build_df(rawdf, p):
    df = add_indicators(rawdf, lr_window=int(p["lr_window"]), trend_window=int(p["trend_window"]))
    return add_signals(df, slope_buy=p["slope_buy"], slope_sell=p["slope_sell"],
                       use_trend_filter=bool(p["use_trend_filter"]))

def run_grid_search(symbol, interval, train_start, train_end, grid, eval_params, asset_type):
    return _run(
        strategy_name="Linear Regression Slope", runs_base="results/linreg",
        symbol=symbol, interval=interval,
        train_start=train_start, train_end=train_end,
        grid=grid, eval_params=eval_params, asset_type=asset_type,
        build_df=_build_df,
        is_valid=lambda p: p["slope_buy"] > 0 and p["slope_sell"] < 0,
        readme_cols=_COLS,
        format_combo=lambda p: f"lr={int(p['lr_window'])} buy={p['slope_buy']} sell={p['slope_sell']} tp={p['tp_pct']} sl={p['sl_pct']}",
    )
