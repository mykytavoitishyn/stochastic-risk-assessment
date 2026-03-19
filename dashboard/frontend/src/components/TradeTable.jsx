export default function TradeTable({ trades }) {
  if (!trades || trades.length === 0) return null;

  return (
    <div className="chart-block">
      <h3>Trades ({trades.length})</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Entry</th>
              <th>Exit</th>
              <th>Dir</th>
              <th>Entry $</th>
              <th>Exit $</th>
              <th>Return %</th>
              <th>PnL</th>
              <th>Candles</th>
              <th>Portfolio</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t, i) => {
              const win = t.pnl > 0;
              return (
                <tr key={i}>
                  <td>{t.entry_time}</td>
                  <td>{t.exit_time}</td>
                  <td style={{ color: t.signal === 1 ? "#3fb950" : "#f85149" }}>
                    {t.signal === 1 ? "Long" : "Short"}
                  </td>
                  <td>${t.entry_price.toLocaleString()}</td>
                  <td>${t.exit_price.toLocaleString()}</td>
                  <td className={win ? "win" : "loss"}>
                    {t.return_pct > 0 ? "+" : ""}
                    {t.return_pct}%
                  </td>
                  <td className={win ? "win" : "loss"}>
                    {win ? "+" : ""}${t.pnl.toLocaleString()}
                  </td>
                  <td>{t.candles}</td>
                  <td>${t.portfolio.toLocaleString()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
