import pandas as pd

from backtesting.shared.load import load_df
from backtesting.shared.trade import simulate_trades, evaluate_trades
from backtesting.shared.result import plot, summarize
from backtesting.shared.validate import latest_run_dir


def run_diagnose(
    strategy_name: str,
    runs_base: str,
    symbol: str,
    interval: str,
    data_start: str,
    data_end: str,
    test_start: str,
    test_end: str,
    eval_params: dict,
    build_df,           # (rawdf_copy, params) -> df with indicators + signals
    make_plot_kwargs,   # (params) -> dict passed to plot()
    run_dir: str = None,
    rank: int = 0,
) -> None:
    if run_dir is None:
        run_dir = latest_run_dir(runs_base)

    p = pd.read_csv(f"{run_dir}/grid_search.csv").iloc[rank]
    print(f"── Diagnose · {strategy_name} · {symbol} {interval}  [test: {test_start} → {test_end}  |  rank-{rank + 1}  sharpe={p['sharpe']:+.2f}  tp={p['tp_pct']}  sl={p['sl_pct']}]")

    TEST_START = pd.to_datetime(test_start)
    TEST_END   = pd.to_datetime(test_end)

    df     = build_df(load_df(ticker=symbol, timeframe=interval, start_date=data_start, end_date=data_end), p)
    df     = df[(df["close_time"] > TEST_START) & (df["close_time"] <= TEST_END)]
    trades = simulate_trades(df, tp_pct=p["tp_pct"], sl_pct=p["sl_pct"], max_candles=int(p["max_candles"]))

    kwargs = make_plot_kwargs(p)
    if trades.empty:
        print("No trades fired.")
        plot(df, **kwargs)
        return

    resdf = evaluate_trades(trades, **eval_params)
    summarize(resdf)
    plot(df, trades=resdf, **kwargs)
