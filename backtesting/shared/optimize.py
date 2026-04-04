import os
import itertools
from datetime import datetime

import pandas as pd
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

from backtesting.shared.load import load_df
from backtesting.shared.trade import simulate_trades, evaluate_trades

_console = Console()


def run_grid_search(
    strategy_name: str,
    runs_base: str,
    symbol: str,
    interval: str,
    train_start: str,
    train_end: str,
    asset_type: str,
    grid: dict,
    eval_params: dict,
    build_df,           # (rawdf_copy, params) -> df with indicators + signals
    is_valid,           # (params) -> bool
    readme_cols: list,
    format_combo=None,  # (params) -> str  — key params for the per-combo progress line
) -> str:
    START = pd.to_datetime(train_start)
    END   = pd.to_datetime(train_end)

    keys   = list(grid.keys())
    combos = [dict(zip(keys, v)) for v in itertools.product(*grid.values()) if is_valid(dict(zip(keys, v)))]
    width  = len(str(len(combos)))

    _console.print(f"[bold]Grid Search[/bold]  ·  {strategy_name}  ·  {symbol} {interval}  [{train_start} → {train_end}  |  {len(combos)} combos]")

    rawdf   = load_df(ticker=symbol, timeframe=interval, asset_type=asset_type)
    results = []

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TextColumn("{task.fields[status]}"),
        console=_console,
        transient=False,
    )

    with progress:
        task = progress.add_task("Running combos", total=len(combos), status="")
        for i, p in enumerate(combos):
            desc = format_combo(p) if format_combo else f"combo {i+1}"
            progress.update(task, description=desc)
            try:
                df     = build_df(rawdf.copy(), p)
                df     = df[(df["close_time"] > START) & (df["close_time"] <= END)]
                trades = simulate_trades(df, tp_pct=p["tp_pct"], sl_pct=p["sl_pct"], max_candles=p["max_candles"])
                if trades.empty:
                    progress.advance(task)
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
                r = results[-1]
                sharpe_style = "green" if r["sharpe"] > 0 else "red"
                progress.update(task, status=f"[{sharpe_style}]sharpe={r['sharpe']:+.2f}[/{sharpe_style}]  wr={r['win_rate']}%  n={r['trades']}")
            except Exception:
                pass
            progress.advance(task)

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

    # ── top results table ─────────────────────────────────────────────────────
    top = df_results.head(10)
    tbl = Table(title=f"Top {len(top)} by Sharpe", box=box.SIMPLE_HEAD, header_style="bold cyan", show_lines=False)
    display_cols = [c for c in ["sharpe", "win_rate", "trades", "total_pnl", "max_drawdown", "avg_candles"] if c in top.columns]
    for c in display_cols:
        tbl.add_column(c, justify="right")
    for _, row in top.iterrows():
        sharpe_val = row.get("sharpe", 0)
        style = "green" if sharpe_val > 0 else "red"
        tbl.add_row(*[f"{row[c]}" for c in display_cols], style=style)
    _console.print(tbl)
    _console.print(f"[dim]Grid search: {len(df_results)} results → {run_dir}[/dim]")
    return run_dir
