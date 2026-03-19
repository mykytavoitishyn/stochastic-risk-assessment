export default function MetricsCard({ metrics }) {
  if (!metrics || !metrics.trade_count) return null;

  const pnlPositive = metrics.total_pnl >= 0;
  const pctReturn = (((metrics.final_portfolio - metrics.init_portfolio) / metrics.init_portfolio) * 100).toFixed(2);

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="label">Final Portfolio</div>
        <div className={`value ${pnlPositive ? "positive" : "negative"}`}>
          ${metrics.final_portfolio.toLocaleString()}
        </div>
      </div>
      <div className="metric-card">
        <div className="label">Total PnL</div>
        <div className={`value ${pnlPositive ? "positive" : "negative"}`}>
          {pnlPositive ? "+" : ""}${metrics.total_pnl.toLocaleString()}
        </div>
      </div>
      <div className="metric-card">
        <div className="label">Return</div>
        <div className={`value ${pnlPositive ? "positive" : "negative"}`}>
          {pnlPositive ? "+" : ""}{pctReturn}%
        </div>
      </div>
      <div className="metric-card">
        <div className="label">Win Rate</div>
        <div className={`value ${metrics.win_rate >= 50 ? "positive" : "negative"}`}>
          {metrics.win_rate}%
        </div>
      </div>
      <div className="metric-card">
        <div className="label">Sharpe</div>
        <div className={`value ${metrics.sharpe > 0 ? "positive" : metrics.sharpe < 0 ? "negative" : "neutral"}`}>
          {metrics.sharpe ?? "—"}
        </div>
      </div>
      <div className="metric-card">
        <div className="label">Trades</div>
        <div className="value neutral">{metrics.trade_count}</div>
      </div>
    </div>
  );
}
