import os
from datetime import datetime

import pandas as pd

from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators, add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades


def _latest_run_dir(runs_base: str) -> str:
    dirs = sorted(
        [d for d in os.listdir(runs_base) if os.path.isfile(f"{runs_base}/{d}/grid_search.csv")],
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError(f"No grid_search.csv found under {runs_base}/. Run grid_search.py first.")
    return f"{runs_base}/{dirs[0]}"


def run_validation(
    symbol: str,
    interval: str,
    data_start: str,
    data_end: str,
    test_start: str,
    test_end: str,
    eval_params: dict,
    run_dir: str = None,
    top_n: int = 10,
) -> pd.DataFrame:
    """Validate top-N grid search configs on the held-out test window.

    If run_dir is None, uses the most recent grid search run.
    Returns a DataFrame of per-config test results and saves CSV + MD to run_dir.
    """
    runs_base = "results/macrossover"
    if run_dir is None:
        run_dir = _latest_run_dir(runs_base)
    print(f"Using run: {run_dir}")

    TEST_START = pd.to_datetime(test_start)
    TEST_END   = pd.to_datetime(test_end)

    train_results = pd.read_csv(f"{run_dir}/grid_search.csv")
    top_configs   = train_results.head(top_n)
    print(f"Validating top {top_n} train configs on held-out test window "
          f"({test_start} → {test_end})...\n")

    rawdf = load_df(ticker=symbol, timeframe=interval, start_date=data_start, end_date=data_end)
    rows  = []

    for _, p in top_configs.iterrows():
        try:
            df = add_indicators(
                rawdf.copy(),
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
                test_sharpe, test_win_rate, test_pnl, test_dd, test_trades = 0, 0, 0, 0, 0
            else:
                ev = evaluate_trades(trades, **eval_params)
                test_trades   = len(ev)
                test_win_rate = round(len(ev[ev["pnl"] > 0]) / len(ev) * 100, 1)
                test_pnl      = round(ev["pnl"].sum(), 2)
                test_sharpe   = ev.attrs.get("sharpe", 0)
                test_dd       = ev.attrs.get("max_drawdown", 0)

            passed = test_sharpe > 0 and test_win_rate > 50 and abs(test_dd) < 20 and test_trades >= 5
            rows.append({
                "short": int(p["short_window"]),
                "long":  int(p["long_window"]),
                "trend": int(p["trend_window"]),
                "rsi_b": p["rsi_buy"],
                "rsi_s": p["rsi_sell"],
                "cp":    int(p["cross_persist"]),
                "tp":    p["tp_pct"],
                "sl":    p["sl_pct"],
                "train_sharpe": round(p["sharpe"], 2),
                "test_sharpe":  test_sharpe,
                "test_wr%":     test_win_rate,
                "test_pnl":     test_pnl,
                "test_dd%":     test_dd,
                "test_n":       test_trades,
                "pass":         "YES" if passed else "no",
            })
        except Exception as e:
            rows.append({"short": int(p["short_window"]), "pass": f"ERROR: {e}"})

    df_out  = pd.DataFrame(rows)
    passing = df_out[df_out["pass"] == "YES"]

    print(df_out.to_string(index=False))
    print(f"\n{'═'*60}")
    print(f"  {len(passing)} / {len(df_out)} configs passed out-of-sample validation")
    print(f"{'═'*60}")

    best_line = ""
    if not passing.empty:
        best = passing.sort_values("test_sharpe", ascending=False).iloc[0]
        best_line = (
            f"\n## Best config\n\n"
            f"```\nshort_window={int(best['short'])}, long_window={int(best['long'])}, "
            f"trend_window={int(best['trend'])}\n"
            f"rsi_buy={best['rsi_b']}, rsi_sell={best['rsi_s']}, cross_persist={int(best['cp'])}\n"
            f"tp_pct={best['tp']}, sl_pct={best['sl']}\n```\n\n"
            f"test Sharpe={best['test_sharpe']}, win_rate={best['test_wr%']}%, drawdown={best['test_dd%']}%"
        )
        print(f"\nBest config:")
        print(f"  short_window={int(best['short'])}, long_window={int(best['long'])}, trend_window={int(best['trend'])}")
        print(f"  rsi_buy={best['rsi_b']}, rsi_sell={best['rsi_s']}, cross_persist={int(best['cp'])}")
        print(f"  tp_pct={best['tp']}, sl_pct={best['sl']}")
        print(f"  → test Sharpe={best['test_sharpe']}, win_rate={best['test_wr%']}%, drawdown={best['test_dd%']}%")

    # ── save results ──────────────────────────────────────────────────────────
    df_out.to_csv(f"{run_dir}/validate.csv", index=False)
    md = f"""# Validation — MA Crossover (out-of-sample)

**Run:** {datetime.now().strftime("%Y-%m-%d")}
**Grid search run:** {run_dir}
**Test window:** {test_start} → {test_end}
**Eval params:** {eval_params}
**Passing configs:** {len(passing)} / {len(df_out)}

A config passes if: test Sharpe > 0, win rate > 50%, drawdown < 20%, trades ≥ 5.

## Results

{df_out.to_markdown(index=False)}
{best_line}
"""
    with open(f"{run_dir}/validate.md", "w") as f:
        f.write(md)
    print(f"\nResults saved to {run_dir}/")

    return df_out
