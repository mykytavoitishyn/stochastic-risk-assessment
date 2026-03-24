import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root)
sys.path.insert(0, root)

import itertools
import pandas as pd
from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators, add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades

# ── data ────────────────────────────────────────────────────────────────────
SYMBOL   = "BTCUSDT"
INTERVAL = "15m"
DATA_PATH = f"data/org/marketdata/{SYMBOL}_{INTERVAL}_2024-03-21_2026-03-21.csv"
START = pd.to_datetime("2025-09-21")
END   = pd.to_datetime("2026-03-21")

# ── param grid ───────────────────────────────────────────────────────────────
GRID = {
    "short_window":  [10, 20, 50],
    "long_window":   [50, 100, 200],
    "trend_window":  [100, 200],
    "rsi_buy":       [55],
    "rsi_sell":      [45],
    "cross_persist": [1],
    "tp_pct":        [0.03, 0.05, 0.08],
    "sl_pct":        [0.01, 0.02, 0.03],
    "use_vol_filter": [True]
}

# filter combos where short >= long
def valid(p):
    return p["short_window"] < p["long_window"] < p["trend_window"]

keys   = list(GRID.keys())
combos = [dict(zip(keys, v)) for v in itertools.product(*GRID.values()) if valid(dict(zip(keys, v)))]
print(f"Running {len(combos)} combinations on {SYMBOL} {INTERVAL}...")

# ── run ──────────────────────────────────────────────────────────────────────
rawdf = load_df(ticker=SYMBOL, timeframe= INTERVAL, start_date="2024-03-21", end_date="2026-03-21")
results = []

for i, p in enumerate(combos):
    try:
        df = add_indicators(
            rawdf.copy(),
            short_window=p["short_window"],
            long_window=p["long_window"],
            trend_window=p["trend_window"]
        )
        df = add_signals(
            df,
            cross_persist=p["cross_persist"],
            rsi_buy=p["rsi_buy"],
            rsi_sell=p["rsi_sell"],
            use_vol_filter=p["use_vol_filter"]
        )
        df = df[(df["close_time"] > START) & (df["close_time"] <= END)]
        trades = simulate_trades(df, tp_pct=p["tp_pct"], sl_pct=p["sl_pct"], max_candles=96)
        if trades.empty:
            continue
        ev = evaluate_trades(trades) # default eval trade params used

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
        
        print(results[-1]["final_portf"])

    except Exception as e:
        continue

    if (i + 1) % 100 == 0:
        print(f"  {i+1}/{len(combos)} done...")

# ── save & display ────────────────────────────────────────────────────────────
os.makedirs("results", exist_ok=True)
df_results = pd.DataFrame(results).sort_values("sharpe", ascending=False)
out_path = "results/grid_search_macrossover.csv"
try:
    df_results.to_csv(out_path, index=False)
except PermissionError:
    from datetime import datetime
    out_path = f"results/grid_search_macrossover_{datetime.now().strftime('%H%M%S')}.csv"
    df_results.to_csv(out_path, index=False)
    print(f"(original file was locked, saved to {out_path})")

print(f"\nDone. {len(df_results)} valid configs saved to {out_path}\n")
print("═" * 60)
print("TOP 10 by Sharpe ratio:")
print("═" * 60)
cols = ["short_window","long_window","trend_window","tp_pct","sl_pct",
        "use_vol_filter","trades","win_rate","total_pnl","sharpe","max_drawdown"]
print(df_results[cols].head(10).to_string(index=False))
