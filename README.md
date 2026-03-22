# Stochastic Agentic Trading System

Human-supervised  Bayesian trading assistant for crypto spot markets.

## Vision

A personal trading assistant that runs 24/7, analyzing crypto markets using Bayesian probabilistic models. Instead of predicting exact prices, it estimates probability distributions over outcomes and proposes sized trades.

The system operates in two modes:

- **Supervised mode** — every trade proposal is routed through a human approval layer before execution
- **Autonomous mode** — the system executes within pre-defined risk boundaries without interruption

The design priority is ease of interaction — switching modes, reviewing signals, and overriding decisions should require minimal effort.

You learn trading by tradings

---

## Backtesting

### Strategy: MA Golden / Death Cross

A trend-following strategy based on two moving average crossovers, filtered by a long-term trend MA and RSI to reduce false entries.

**Entry logic:**

- **Golden cross (BUY):** Short MA crosses above Long MA, sustained for `cross_persist` candles, price is above Trend MA, and RSI is not overbought (`rsi ≤ rsi_buy`)
- **Death cross (SELL):** Short MA crosses below Long MA, sustained for `cross_persist` candles, price is below Trend MA, and RSI is not oversold (`rsi ≥ rsi_sell`)

**Exit logic (whichever triggers first):**

- Take-profit hits (`tp_pct`)
- Stop-loss hits (`sl_pct`)
- Max holding period reached (`max_candles`)
- Opposite signal fires (reversal)

**Enhancements over vanilla MA cross:**

- Trend filter (MA-trend) prevents trading against the macro direction
- RSI filter avoids chasing overbought/oversold entries
- Volume confirmation: entry only when volume is above its rolling average

**Parameters (grid-searched):**

| Parameter      | Description                      | Default |
| -------------- | -------------------------------- | ------- |
| `short_window` | Short MA period                  | 10      |
| `long_window`  | Long MA period                   | 20      |
| `trend_window` | Trend MA period                  | 100     |
| `rsi_window`   | RSI period                       | 14      |
| `cross_persist`| Candles cross must hold          | 1       |
| `rsi_buy`      | RSI upper threshold for buy      | 55      |
| `rsi_sell`     | RSI lower threshold for sell     | 45      |
| `tp_pct`       | Take-profit %                    | 5%      |
| `sl_pct`       | Stop-loss %                      | 2%      |
| `max_candles`  | Max hold in candles              | 96      |

**Run a single backtest:**

```bash
python backtesting/macrossover/run.py
```

**Run grid search:**

```bash
python backtesting/macrossover/grid_search.py
```

Results saved to `results/grid_search_macrossover.csv`.

### Terminal 1 — backend

cd /home/mykyta/Code/personal/stochastic-risk-assessment
.venv/bin/uvicorn api.main:app --reload --port 8000

### Terminal 2 — frontend

cd dashboard && npm run dev
