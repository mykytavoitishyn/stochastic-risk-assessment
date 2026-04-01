import os
import itertools
from datetime import datetime

import pandas as pd

from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators, add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades


def run_grid_search(
    symbol: str,
    interval: str,
    data_start: str,
    data_end: str,
    train_start: str,
    train_end: str,
    grid: dict,
    eval_params: dict,
) -> str:
    """Run grid search over train window. Returns the run directory path."""
    START = pd.to_datetime(train_start)
    END   = pd.to_datetime(train_end)

    def valid(p):
        return p["short_window"] < p["long_window"] < p["trend_window"]

    keys   = list(grid.keys())
    combos = [dict(zip(keys, v)) for v in itertools.product(*grid.values()) if valid(dict(zip(keys, v)))]
    print(f"Running {len(combos)} combinations on {symbol} {interval} "
          f"({train_start} → {train_end})...")

    rawdf = load_df(ticker=symbol, timeframe=interval, start_date=data_start, end_date=data_end)
    results = []

    for i, p in enumerate(combos):
        try:
            df = add_indicators(
                rawdf.copy(),
                short_window=p["short_window"],
                long_window=p["long_window"],
                trend_window=p["trend_window"],
            )
            df = add_signals(
                df,
                cross_persist=p["cross_persist"],
                rsi_buy=p["rsi_buy"],
                rsi_sell=p["rsi_sell"],
                use_vol_filter=p["use_vol_filter"],
            )
            df = df[(df["close_time"] > START) & (df["close_time"] <= END)]
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
            pct = round((results[-1]["final_portf"] - eval_params["init_portfolio"]) / eval_params["init_portfolio"] * 100, 1)
            print(f"  [{i+1}/{len(combos)}] Final portfolio: {results[-1]['final_portf']} ({pct:+.1f}%)")

        except Exception:
            continue

    # ── create run directory ──────────────────────────────────────────────────
    runs_base = "results/macrossover"
    os.makedirs(runs_base, exist_ok=True)
    prefix = f"{datetime.now().strftime('%Y%m%d')}_{symbol}_{interval}_"
    existing = [d for d in os.listdir(runs_base) if d.startswith(prefix)]
    run_dir = f"{runs_base}/{prefix}{len(existing) + 1:02d}"
    os.makedirs(run_dir)

    df_results = pd.DataFrame(results).sort_values("sharpe", ascending=False)
    df_results.to_csv(f"{run_dir}/grid_search.csv", index=False)

    # ── README ────────────────────────────────────────────────────────────────
    top10 = df_results.head(10)
    cols  = ["short_window", "long_window", "trend_window", "tp_pct", "sl_pct",
             "use_vol_filter", "trades", "win_rate", "total_pnl", "sharpe", "max_drawdown"]
    md = f"""# Grid Search — MA Crossover

**Run:** {datetime.now().strftime("%Y-%m-%d")}
**Strategy:** MA Crossover
**Symbol:** {symbol} / {interval}
**Train window:** {train_start} → {train_end}
**Eval params:** {eval_params}

## Grid searched

| Param | Values |
|---|---|
""" + "\n".join(f"| {k} | {v} |" for k, v in grid.items()) + f"""

**Valid combos:** {len(combos)} | **Results:** {len(df_results)}

## Top 10 by Sharpe

{top10[cols].to_markdown(index=False)}
"""
    with open(f"{run_dir}/README.md", "w") as f:
        f.write(md)

    print(f"\nDone. {len(df_results)} valid configs saved to {run_dir}/")
    print("═" * 60)
    print("TOP 10 by Sharpe ratio:")
    print("═" * 60)
    print(top10[cols].to_string(index=False))

    return run_dir
