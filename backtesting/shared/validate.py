import os
from datetime import datetime

import pandas as pd
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from backtesting.shared.load import load_df
from backtesting.shared.trade import simulate_trades, evaluate_trades

_console = Console()


def latest_run_dir(runs_base: str) -> str:
    dirs = sorted(
        [d for d in os.listdir(runs_base) if os.path.isfile(f"{runs_base}/{d}/grid_search.csv")],
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError(f"No grid_search.csv found under {runs_base}/. Run grid_search.py first.")
    return f"{runs_base}/{dirs[0]}"


def run_validation(
    strategy_name: str,
    runs_base: str,
    symbol: str,
    interval: str,
    test_start: str,
    test_end: str,
    eval_params: dict,
    asset_type: str,
    build_df,          # (rawdf_copy, params) -> df with indicators + signals
    make_param_row,    # (params) -> dict of strategy-specific columns for the output row
    format_best,       # (best_row) -> str describing the best config (for MD)
    run_dir: str = None,
    top_n: int = 10,
) -> pd.DataFrame:
    if run_dir is None:
        run_dir = latest_run_dir(runs_base)

    _console.print(f"[bold]Validation[/bold]  ·  {strategy_name}  ·  {symbol} {interval}  [test: {test_start} → {test_end}]")

    TEST_START = pd.to_datetime(test_start)
    TEST_END   = pd.to_datetime(test_end)

    top_configs = pd.read_csv(f"{run_dir}/grid_search.csv").head(top_n)
    rawdf       = load_df(ticker=symbol, timeframe=interval, asset_type=asset_type)
    rows        = []

    for _, p in top_configs.iterrows():
        try:
            df     = build_df(rawdf.copy(), p)
            df     = df[(df["close_time"] > TEST_START) & (df["close_time"] <= TEST_END)]
            trades = simulate_trades(df, tp_pct=p["tp_pct"], sl_pct=p["sl_pct"], max_candles=int(p["max_candles"]))

            if trades.empty:
                test_sharpe, test_win_rate, test_pnl, test_dd, test_n = 0, 0, 0, 0, 0
            else:
                ev            = evaluate_trades(trades, **eval_params)
                test_n        = len(ev)
                test_win_rate = round(len(ev[ev["pnl"] > 0]) / len(ev) * 100, 1)
                test_pnl      = round(ev["pnl"].sum(), 2)
                test_sharpe   = ev.attrs.get("sharpe", 0)
                test_dd       = ev.attrs.get("max_drawdown", 0)

            passed = test_sharpe > 0 and test_win_rate > 50 and abs(test_dd) < 20 and test_n >= 5
            rows.append({
                **make_param_row(p),
                "train_sharpe": round(p["sharpe"], 2),
                "test_sharpe":  test_sharpe,
                "test_wr%":     test_win_rate,
                "test_pnl":     test_pnl,
                "test_dd%":     test_dd,
                "test_n":       test_n,
                "pass":         "YES" if passed else "no",
            })
        except Exception as e:
            rows.append({"pass": f"ERROR: {e}"})

    df_out  = pd.DataFrame(rows)
    passing = df_out[df_out["pass"] == "YES"]

    # ── results table ─────────────────────────────────────────────────────────
    display_cols = [c for c in df_out.columns if c != "pass"]
    tbl = Table(box=box.SIMPLE_HEAD, header_style="bold cyan", show_lines=False)
    for c in display_cols:
        tbl.add_column(c, justify="right")
    tbl.add_column("pass", justify="center")
    for _, row in df_out.iterrows():
        passed = row.get("pass") == "YES"
        row_style = "green" if passed else ""
        tbl.add_row(
            *[str(row[c]) for c in display_cols],
            Text("YES", style="bold green") if passed else Text("no", style="dim"),
            style=row_style,
        )
    pass_style = "green" if len(passing) > 0 else "red"
    _console.print(Panel(
        tbl,
        title=f"[bold]Validation Results[/bold]  [{test_start} → {test_end}]",
        subtitle=Text(f"{len(passing)}/{len(df_out)} passed", style=f"bold {pass_style}"),
        border_style="bright_blue",
        padding=(0, 1),
    ))

    best_block = ""
    if not passing.empty:
        best       = passing.sort_values("test_sharpe", ascending=False).iloc[0]
        best_block = f"\n## Best config\n\n```\n{format_best(best)}\n```\n\nSharpe={best['test_sharpe']}, win_rate={best['test_wr%']}%, drawdown={best['test_dd%']}%\n"

    _console.print(f"[dim]Saved → {run_dir}/validate.csv[/dim]")
    df_out.to_csv(f"{run_dir}/validate.csv", index=False)
    md = (
        f"# Validation — {strategy_name}\n\n"
        f"**Test window:** {test_start} → {test_end} | **Passing:** {len(passing)}/{len(df_out)}\n\n"
        f"Pass criteria: Sharpe > 0, win rate > 50%, drawdown < 20%, trades ≥ 5.\n\n"
        f"## Results\n\n{df_out.to_markdown(index=False)}\n"
        + best_block
    )
    with open(f"{run_dir}/validate.md", "w") as f:
        f.write(md)

    return df_out
