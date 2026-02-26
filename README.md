# Stochastic Agentic Trading System

Human-supervised  Bayesian trading assistant for crypto spot markets.

## Vision

A personal trading assistant that runs 24/7, analyzing crypto markets using Bayesian probabilistic models. Instead of predicting exact prices, it estimates probability distributions over outcomes and proposes sized trades.

The system operates in two modes:

- **Supervised mode** — every trade proposal is routed through a human approval layer before execution
- **Autonomous mode** — the system executes within pre-defined risk boundaries without interruption

The design priority is ease of interaction — switching modes, reviewing signals, and overriding decisions should require minimal effort.

## MVP Timeline

| Phase | Period | Goal |
|---|---|---|
| **Build** | Mar 2026 - Dec 2026 | Core system development, backtesting, signal validation |
| **Testnet** | Jan 2027 | Full pipeline live on Binance testnet, no real money |
| **Validate** | Jan 2027 - Mar 2027 | 50+ simulated trades, Bayesian posteriors updating correctly |
| **Real money (small)** | Apr 2027 | Deploy €1,000 to live spot, 1% risk per trade |
| **Scale** | Jul 2027 | Scale to €5,000 if live performance tracks testnet |
| **Evaluate** | Jun 2027+ | Assess outcomes, decide next phase based on real data |

Phase gates are strict — the next phase only starts if the previous one proves positive expected value.