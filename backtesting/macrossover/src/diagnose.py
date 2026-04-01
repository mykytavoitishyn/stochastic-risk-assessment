import os

import pandas as pd

from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators, add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades
from backtesting.macrossover.src.result import plot, summarize


def _latest_run_dir(runs_base: str) -> str:
    dirs = sorted(
        [d for d in os.listdir(runs_base) if os.path.isfile(f"{runs_base}/{d}/grid_search.csv")],
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError(f"No grid_search.csv found under {runs_base}/. Run grid_search.py first.")
    return f"{runs_base}/{dirs[0]}"


def run_diagnose(
    symbol: str,
    interval: str,
    data_start: str,
    data_end: str,
    test_start: str,
    test_end: str,
    eval_params: dict,
    run_dir: str = None,
    rank: int = 0,
) -> None:
    """Visualise and summarise the rank-th best train config on the test window.

    rank=0 is the best config by Sharpe, rank=1 second-best, etc.
    Useful for understanding *why* a config failed out-of-sample.
    """
    runs_base = "results/macrossover"
    if run_dir is None:
        run_dir = _latest_run_dir(runs_base)
    print(f"Using run: {run_dir}")

    grid_results = pd.read_csv(f"{run_dir}/grid_search.csv")
    p = grid_results.iloc[rank]

    print(f"\nDiagnosing rank-{rank + 1} train config (train Sharpe={p['sharpe']}):")
    print(f"  short={int(p['short_window'])}  long={int(p['long_window'])}  trend={int(p['trend_window'])}")
    print(f"  rsi_buy={p['rsi_buy']}  rsi_sell={p['rsi_sell']}  cross_persist={int(p['cross_persist'])}")
    print(f"  tp={p['tp_pct']}  sl={p['sl_pct']}  vol_filter={p['use_vol_filter']}")
    print(f"\nTest window: {test_start} → {test_end}\n")

    TEST_START = pd.to_datetime(test_start)
    TEST_END   = pd.to_datetime(test_end)

    df = load_df(ticker=symbol, timeframe=interval, start_date=data_start, end_date=data_end)
    df = add_indicators(
        df,
        short_window=int(p["short_window"]),
        long_window=int(p["long_window"]),
        trend_window=int(p["trend_window"]),
    )
    df = add_signals(
        df,
        cross_persist=int(p["cross_persist"]),
        rsi_buy=p["rsi_buy"],
        rsi_sell=p["rsi_sell"],
        use_vol_filter=bool(p["use_vol_filter"]),
    )
    df = df[(df["close_time"] > TEST_START) & (df["close_time"] <= TEST_END)]

    trades = simulate_trades(df, tp_pct=p["tp_pct"], sl_pct=p["sl_pct"], max_candles=int(p["max_candles"]))

    if trades.empty:
        print("No trades fired in the test window — signals never triggered.")
        plot(df)
        return

    resdf = evaluate_trades(trades, **eval_params)
    summarize(resdf)
    plot(df, trades=resdf)
