import os
import sys
import glob as glob_module

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backtesting"))

from ma_crossover_playaround import (
    load_df, add_indicators, add_signals, simulate_trades, sharpe_ratio, run_grid_search,
)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def safe_float(v):
    try:
        f = float(v)
        return None if (f != f or f == float("inf") or f == float("-inf")) else f
    except Exception:
        return None


@app.get("/api/data-files")
def list_data_files():
    files = sorted(glob_module.glob("data/org/marketdata/*.csv"))
    return {"files": files}


class RunParams(BaseModel):
    filepath: str
    start_date: str
    end_date: str
    short_window: int = 20
    long_window: int = 50
    trend_window: int = 200
    rsi_window: int = 14
    cross_persist: int = 2
    rsi_buy: int = 55
    rsi_sell: int = 45
    init_portfolio: float = 1000
    trade_size_pct: float = 0.1
    fee_pct: float = 0.0005
    leverage: int = 10


@app.post("/api/run")
def run_backtest(params: RunParams):
    try:
        df = load_df(params.filepath, params.start_date, params.end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    df = add_indicators(df, params.short_window, params.long_window, params.trend_window, params.rsi_window)
    df = add_signals(df, params.cross_persist, params.rsi_buy, params.rsi_sell)
    trades = simulate_trades(df, params.init_portfolio, params.trade_size_pct, params.fee_pct, params.leverage)

    # Downsample chart data for performance (keep max 1500 points)
    step = max(1, len(df) // 1500)
    df_chart = df.iloc[::step]

    chart_data = [
        {
            "date": int(row["open_time"].timestamp() * 1000),
            "close": safe_float(row["close_price"]),
            "ma_short": safe_float(row["ma_short"]),
            "ma_long": safe_float(row["ma_long"]),
            "ma_trend": safe_float(row["ma_trend"]),
            "rsi": safe_float(row["rsi"]),
        }
        for _, row in df_chart.iterrows()
    ]

    metrics = {}
    trades_list = []
    trade_markers = []
    portfolio_curve = []

    if not trades.empty:
        trades_sorted = trades.sort_values("entry_time").copy()
        total_pnl = float(trades_sorted["pnl"].sum())
        win_rate = float((trades_sorted["pnl"] > 0).mean())
        sharpe = sharpe_ratio(trades_sorted)

        metrics = {
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate * 100, 1),
            "sharpe": round(float(sharpe), 3) if sharpe == sharpe else None,
            "final_portfolio": round(float(trades_sorted["portfolio"].iloc[-1]), 2),
            "trade_count": len(trades_sorted),
            "init_portfolio": params.init_portfolio,
        }

        for _, t in trades_sorted.iterrows():
            entry_ts = int(t["entry_time"].timestamp() * 1000)
            exit_ts = int(t["exit_time"].timestamp() * 1000)
            trades_list.append({
                "entry_time": t["entry_time"].strftime("%Y-%m-%d %H:%M"),
                "exit_time": t["exit_time"].strftime("%Y-%m-%d %H:%M"),
                "entry_price": round(float(t["entry_price"]), 2),
                "exit_price": round(float(t["exit_price"]), 2),
                "signal": int(t["signal"]),
                "return_pct": round(float(t["return"]) * 100, 3),
                "pnl": round(float(t["pnl"]), 2),
                "candles": int(t["candles"]),
                "portfolio": round(float(t["portfolio"]), 2),
            })
            trade_markers.append({
                "date": entry_ts,
                "price": round(float(t["entry_price"]), 2),
                "type": "buy" if int(t["signal"]) == 1 else "sell",
            })
            portfolio_curve.append({"date": exit_ts, "portfolio": round(float(t["portfolio"]), 2)})

    return {
        "metrics": metrics,
        "chart_data": chart_data,
        "trades": trades_list,
        "trade_markers": trade_markers,
        "portfolio_curve": portfolio_curve,
    }


class GridParams(BaseModel):
    filepath: str
    start_date: str
    end_date: str
    short_windows: List[int] = [10, 20, 30]
    long_windows: List[int] = [50, 70, 100]
    trend_windows: List[int] = [100, 200]
    cross_persist: List[int] = [1, 2, 3, 4]
    trade_size_pcts: List[float] = [0.02, 0.05, 0.1]
    rsi_buy: int = 55
    rsi_sell: int = 45
    rsi_window: int = 14
    fee_pct: float = 0.0005
    leverage: int = 1
    init_portfolio: float = 1000


@app.post("/api/grid-search")
def grid_search(params: GridParams):
    _, _, all_results = run_grid_search(
        filepath=params.filepath,
        short_windows=params.short_windows,
        long_windows=params.long_windows,
        trend_windows=params.trend_windows,
        cross_persist=params.cross_persist,
        rsi_buy=params.rsi_buy,
        rsi_sell=params.rsi_sell,
        rsi_window=params.rsi_window,
        trade_size_pcts=params.trade_size_pcts,
        fee_pct=params.fee_pct,
        leverage=params.leverage,
        init_portfolio=params.init_portfolio,
        start_date=params.start_date,
        end_date=params.end_date,
    )

    sorted_results = sorted(all_results, key=lambda x: x["final_portfolio"], reverse=True)
    return {
        "all_results": sorted_results,
        "best_result": sorted_results[0] if sorted_results else None,
    }
