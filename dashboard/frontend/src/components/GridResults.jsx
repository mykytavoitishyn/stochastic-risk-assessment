export default function GridResults({ results, bestResult }) {
  if (!results || results.length === 0) return null;

  return (
    <>
      {bestResult && (
        <div className="grid-best">
          <h3>Best Configuration</h3>
          <div className="grid-best-params">
            {Object.entries(bestResult).map(([k, v]) => (
              <div key={k} className="param-badge">
                {k}: <span>{v ?? "—"}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="chart-block">
        <h3>All Results ({results.length} combinations, sorted by portfolio)</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Short</th>
                <th>Long</th>
                <th>Trend</th>
                <th>Persist</th>
                <th>Size %</th>
                <th>Portfolio</th>
                <th>Return %</th>
                <th>Trades</th>
                <th>Win %</th>
                <th>Sharpe</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, i) => {
                const win = r.final_portfolio > (results[0]?.final_portfolio > 0 ? 1000 : 0);
                const pos = r.pct_return >= 0;
                return (
                  <tr key={i} className={i === 0 ? "grid-rank-1" : ""}>
                    <td>{i + 1}</td>
                    <td>{r.short_window}</td>
                    <td>{r.long_window}</td>
                    <td>{r.trend_window}</td>
                    <td>{r.cross_persist}</td>
                    <td>{(r.trade_size_pct * 100).toFixed(0)}%</td>
                    <td>${r.final_portfolio.toLocaleString()}</td>
                    <td style={{ color: pos ? "#3fb950" : "#f85149" }}>
                      {pos ? "+" : ""}{r.pct_return}%
                    </td>
                    <td>{r.trade_count}</td>
                    <td>{r.win_rate_pct}%</td>
                    <td>{r.sharpe ?? "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
