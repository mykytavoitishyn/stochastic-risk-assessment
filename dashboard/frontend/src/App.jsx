import { useState } from "react";
import StrategyForm from "./components/StrategyForm";
import GridSearchForm from "./components/GridSearchForm";
import MetricsCard from "./components/MetricsCard";
import { PriceChart, RSIChart, PortfolioChart } from "./components/Charts";
import TradeTable from "./components/TradeTable";
import GridResults from "./components/GridResults";

export default function App() {
  const [tab, setTab] = useState("run");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [runResult, setRunResult] = useState(null);
  const [gridResult, setGridResult] = useState(null);

  const handleRun = async (params) => {
    setLoading(true);
    setError(null);
    setRunResult(null);
    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Server error");
      }
      setRunResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGridSearch = async (params) => {
    setLoading(true);
    setError(null);
    setGridResult(null);
    try {
      const res = await fetch("/api/grid-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Server error");
      }
      setGridResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="header">
        <h1>Strategy Dashboard</h1>
        <div className="tabs">
          <button className={`tab ${tab === "run" ? "active" : ""}`} onClick={() => setTab("run")}>
            Single Run
          </button>
          <button className={`tab ${tab === "grid" ? "active" : ""}`} onClick={() => setTab("grid")}>
            Grid Search
          </button>
        </div>
      </div>

      <div className="layout">
        <div className="sidebar">
          {tab === "run" ? (
            <StrategyForm onRun={handleRun} loading={loading} />
          ) : (
            <GridSearchForm onRun={handleGridSearch} loading={loading} />
          )}
        </div>

        <div className="main">
          {error && <div className="error">{error}</div>}

          {tab === "run" && (
            <>
              {loading && <div className="loading">Running backtest…</div>}
              {!loading && !runResult && (
                <div className="empty-state">
                  <span>Configure parameters and run a backtest</span>
                </div>
              )}
              {runResult && (
                <>
                  <MetricsCard metrics={runResult.metrics} />
                  <PriceChart chartData={runResult.chart_data} tradeMarkers={runResult.trade_markers} />
                  <RSIChart chartData={runResult.chart_data} />
                  <PortfolioChart
                    portfolioCurve={runResult.portfolio_curve}
                    initPortfolio={runResult.metrics.init_portfolio}
                  />
                  <TradeTable trades={runResult.trades} />
                </>
              )}
            </>
          )}

          {tab === "grid" && (
            <>
              {loading && <div className="loading">Running grid search… (check terminal for progress)</div>}
              {!loading && !gridResult && (
                <div className="empty-state">
                  <span>Configure search space and run grid search</span>
                </div>
              )}
              {gridResult && (
                <GridResults results={gridResult.all_results} bestResult={gridResult.best_result} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
