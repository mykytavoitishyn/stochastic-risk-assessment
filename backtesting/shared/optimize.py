import os
import itertools
from datetime import datetime

import pandas as pd

from backtesting.shared.load import load_df
from backtesting.shared.trade import simulate_trades, evaluate_trades


def run_grid_search(
    strategy_name: str,
    runs_base: str,
    symbol: str,
    interval: str,
    data_start: str,
    data_end: str,
    train_start: str,
    train_end: str,
    grid: dict,
    eval_params: dict,
    build_df,       # (rawdf_copy, params) -> df with indicators + signals
    is_valid,       # (params) -> bool
    readme_cols: list,
) -> str:
    START = pd.to_datetime(train_start)
    END   = pd.to_datetime(train_end)

    keys   = list(grid.keys())
    combos = [dict(zip(keys, v)) for v in itertools.product(*grid.values()) if is_valid(dict(zip(keys, v)))]

    rawdf   = load_df(ticker=symbol, timeframe=interval, start_date=data_start, end_date=data_end)
    results = []

    for p in combos:
        try:
            df     = build_df(rawdf.copy(), p)
            df     = df[(df["close_time"] > START) & (df["close_time"] <= END)]
            trades = simulate_trades(df, tp_pct=p["tp_pct"], sl_pct=p["sl_pct"], max_candles=p["max_candles"])
            if trades.empty:
                continue
            ev = evaluate_trades(trades, **eval_params)
            results.append({
                **p,
                "trades":       len(ev),
                "win_rate":     round(len(ev[ev["pnl"] > 0]) / len(ev) * 100, 1),
                "total_pnl":    round(ev["pnl"].sum(), 2),
                "final_portf":  ev.attrs.get("final_portfolio", 0),
                "sharpe":       ev.attrs.get("sharpe", 0),
                "max_drawdown": ev.attrs.get("max_drawdown", 0),
                "avg_candles":  round(ev["candles"].mean(), 1),
            })
        except Exception:
            continue

    os.makedirs(runs_base, exist_ok=True)
    prefix   = f"{datetime.now().strftime('%Y%m%d')}_{symbol}_{interval}_"
    existing = [d for d in os.listdir(runs_base) if d.startswith(prefix)]
    run_dir  = f"{runs_base}/{prefix}{len(existing) + 1:02d}"
    os.makedirs(run_dir)

    df_results = pd.DataFrame(results).sort_values("sharpe", ascending=False)
    df_results.to_csv(f"{run_dir}/grid_search.csv", index=False)

    top10 = df_results.head(10)
    valid_cols = [c for c in readme_cols if c in df_results.columns]
    md = (
        f"# Grid Search — {strategy_name}\n\n"
        f"**Symbol:** {symbol} / {interval} | **Train:** {train_start} → {train_end}\n\n"
        f"| Param | Values |\n|---|---|\n"
        + "\n".join(f"| {k} | {v} |" for k, v in grid.items())
        + f"\n\n**Combos:** {len(combos)} | **Results:** {len(df_results)}\n\n"
        f"## Top 10 by Sharpe\n\n{top10[valid_cols].to_markdown(index=False)}\n"
    )
    with open(f"{run_dir}/README.md", "w") as f:
        f.write(md)

    print(f"Grid search: {len(df_results)} results → {run_dir}")
    return run_dir
