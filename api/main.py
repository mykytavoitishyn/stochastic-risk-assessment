import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import glob
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from backtesting.macrossover.src.load import load_df
from backtesting.macrossover.src.ta import add_indicators, add_signals
from backtesting.macrossover.src.trade import simulate_trades, evaluate_trades

from src.marketdata import (
    get_balance,
    get_open_orders,
    get_my_trades,
    get_klines,
    get_klines_df,
)

load_dotenv()

API_KEY    = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")
BASE_URL   = "https://testnet.binance.vision"
BINANCE_PUBLIC = "https://api.binance.com"

app = FastAPI(title="Trading Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "org", "marketdata")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")


class BacktestParams(BaseModel):
    symbol: str = "BTCUSDT"
    interval: str = "15m"
    start_date: str = "2025-01-01"
    end_date: str = "2026-03-21"
    short_window: int = 10
    long_window: int = 20
    trend_window: int = 100
    rsi_window: int = 14
    cross_persist: int = 1
    rsi_buy: float = 55
    rsi_sell: float = 45
    use_vol_filter: bool = True
    tp_pct: float = 0.05
    sl_pct: float = 0.02
    max_candles: int = 96
    init_portfolio: float = 1000
    trade_size_pct: float = 0.1
    fee_pct: float = 0.005
    leverage: float = 10


@app.get("/api/balance")
def balance():
    try:
        usdt = get_balance(API_KEY, API_SECRET, asset="USDT", base_url=BASE_URL)
        btc  = get_balance(API_KEY, API_SECRET, asset="BTC",  base_url=BASE_URL)
        return {"USDT": usdt, "BTC": btc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/open-orders")
def open_orders(symbol: str = "BTCUSDT"):
    try:
        orders = get_open_orders(API_KEY, API_SECRET, symbol=symbol, base_url=BASE_URL)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trades")
def trades(symbol: str = "BTCUSDT", limit: int = 50):
    try:
        data = get_my_trades(API_KEY, API_SECRET, symbol=symbol, limit=limit, base_url=BASE_URL)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ticker")
def ticker(symbol: str = "BTCUSDT"):
    try:
        response = requests.get(
            f"{BINANCE_PUBLIC}/api/v3/ticker/24hr",
            params={"symbol": symbol},
            timeout=10,
        )
        response.raise_for_status()
        d = response.json()
        return {
            "symbol": d["symbol"],
            "price": float(d["lastPrice"]),
            "price_change_pct": float(d["priceChangePercent"]),
            "high": float(d["highPrice"]),
            "low": float(d["lowPrice"]),
            "volume": float(d["volume"]),
            "quote_volume": float(d["quoteVolume"]),
            "trades": int(d["count"]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/klines")
def klines(symbol: str = "BTCUSDT", interval: str = "15m", limit: int = 100):
    try:
        raw = get_klines(BINANCE_PUBLIC, symbol, interval)
        if raw is None:
            raise HTTPException(status_code=500, detail="Failed to fetch klines")
        df = get_klines_df(raw[-limit:])
        return df[["open_time", "open_price", "high_price", "low_price", "close_price", "volume"]].assign(
            open_time=df["open_time"].astype(str)
        ).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/backtest/datasets")
def backtest_datasets():
    """List available CSV datasets."""
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    return [os.path.basename(f) for f in sorted(files)]


@app.post("/api/backtest/run")
def backtest_run(p: BacktestParams):
    """Run a single backtest with given params. Returns summary + trade list."""
    try:
        path = os.path.join(DATA_DIR, f"{p.symbol}_{p.interval}_2024-03-21_2026-03-21.csv")
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Dataset not found: {os.path.basename(path)}")

        rawdf = load_df(path, start_date=pd.to_datetime(p.start_date), end_date=pd.to_datetime(p.end_date))
        df = add_indicators(rawdf, short_window=p.short_window, long_window=p.long_window,
                            trend_window=p.trend_window, rsi_window=p.rsi_window)
        df = add_signals(df, cross_persist=p.cross_persist, rsi_buy=p.rsi_buy,
                         rsi_sell=p.rsi_sell, use_vol_filter=p.use_vol_filter)
        trades = simulate_trades(df, tp_pct=p.tp_pct, sl_pct=p.sl_pct, max_candles=p.max_candles)

        if trades.empty:
            return {"summary": {"trades": 0}, "trades": [], "portfolio_curve": []}

        ev = evaluate_trades(trades, init_portfolio=p.init_portfolio,
                             trade_size_pct=p.trade_size_pct, fee_pct=p.fee_pct, leverage=p.leverage)

        wins = ev[ev["pnl"] > 0]
        summary = {
            "trades":        len(ev),
            "win_rate":      round(len(wins) / len(ev) * 100, 1),
            "total_pnl":     round(ev["pnl"].sum(), 2),
            "final_portfolio": round(ev["portfolio"].iloc[-1], 2),
            "avg_pnl":       round(ev["pnl"].mean(), 2),
            "best_trade":    round(ev["pnl"].max(), 2),
            "worst_trade":   round(ev["pnl"].min(), 2),
            "avg_candles":   round(ev["candles"].mean(), 1),
            "sharpe":        ev.attrs.get("sharpe", 0),
            "max_drawdown":  ev.attrs.get("max_drawdown", 0),
            "exit_reasons":  ev["exit_reason"].value_counts().to_dict(),
        }

        trades_out = ev[["entry_time", "exit_time", "entry_price", "exit_price",
                          "signal", "candles", "exit_reason", "pnl", "portfolio"]].copy()
        trades_out["entry_time"] = trades_out["entry_time"].astype(str)
        trades_out["exit_time"]  = trades_out["exit_time"].astype(str)
        trades_out["side"]       = trades_out["signal"].map({1: "BUY", -1: "SELL"})

        curve = ev[["entry_time", "portfolio"]].copy()
        curve["entry_time"] = curve["entry_time"].astype(str)

        return {
            "summary": summary,
            "trades":  trades_out.to_dict(orient="records"),
            "portfolio_curve": curve.rename(columns={"entry_time": "time"}).to_dict(orient="records"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/backtest/grid-results")
def backtest_grid_results():
    """Return the latest grid search CSV as JSON, sorted by Sharpe."""
    path = os.path.join(RESULTS_DIR, "grid_search_macrossover.csv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path).sort_values("sharpe", ascending=False)
    return df.head(50).to_dict(orient="records")
