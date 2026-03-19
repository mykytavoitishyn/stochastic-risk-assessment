import { useState, useEffect } from "react";

const defaults = {
  filepath: "",
  start_date: "2026-01-01",
  end_date: "2026-03-01",
  short_window: 20,
  long_window: 50,
  trend_window: 200,
  rsi_window: 14,
  cross_persist: 2,
  rsi_buy: 55,
  rsi_sell: 45,
  init_portfolio: 1000,
  trade_size_pct: 0.1,
  fee_pct: 0.0005,
  leverage: 10,
};

export default function StrategyForm({ onRun, loading }) {
  const [params, setParams] = useState(defaults);
  const [files, setFiles] = useState([]);

  useEffect(() => {
    fetch("/api/data-files")
      .then((r) => r.json())
      .then((d) => {
        setFiles(d.files);
        if (d.files.length > 0) setParams((p) => ({ ...p, filepath: d.files[0] }));
      });
  }, []);

  const set = (k) => (e) => setParams((p) => ({ ...p, [k]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onRun({
      ...params,
      short_window: +params.short_window,
      long_window: +params.long_window,
      trend_window: +params.trend_window,
      rsi_window: +params.rsi_window,
      cross_persist: +params.cross_persist,
      rsi_buy: +params.rsi_buy,
      rsi_sell: +params.rsi_sell,
      init_portfolio: +params.init_portfolio,
      trade_size_pct: +params.trade_size_pct,
      fee_pct: +params.fee_pct,
      leverage: +params.leverage,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-section">
        <h3>Data</h3>
        <div className="field">
          <label>File</label>
          <select value={params.filepath} onChange={set("filepath")}>
            {files.map((f) => (
              <option key={f} value={f}>{f.split("/").pop()}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Start date</label>
          <input type="date" value={params.start_date} onChange={set("start_date")} />
        </div>
        <div className="field">
          <label>End date</label>
          <input type="date" value={params.end_date} onChange={set("end_date")} />
        </div>
      </div>

      <div className="form-section">
        <h3>Moving Averages</h3>
        <div className="field">
          <label>Short window</label>
          <input type="number" value={params.short_window} onChange={set("short_window")} min={2} />
        </div>
        <div className="field">
          <label>Long window</label>
          <input type="number" value={params.long_window} onChange={set("long_window")} min={2} />
        </div>
        <div className="field">
          <label>Trend window</label>
          <input type="number" value={params.trend_window} onChange={set("trend_window")} min={2} />
        </div>
      </div>

      <div className="form-section">
        <h3>Signals</h3>
        <div className="field">
          <label>RSI window</label>
          <input type="number" value={params.rsi_window} onChange={set("rsi_window")} min={2} />
        </div>
        <div className="field">
          <label>Cross persist (candles)</label>
          <input type="number" value={params.cross_persist} onChange={set("cross_persist")} min={1} />
        </div>
        <div className="field">
          <label>RSI buy threshold</label>
          <input type="number" value={params.rsi_buy} onChange={set("rsi_buy")} />
        </div>
        <div className="field">
          <label>RSI sell threshold</label>
          <input type="number" value={params.rsi_sell} onChange={set("rsi_sell")} />
        </div>
      </div>

      <div className="form-section">
        <h3>Portfolio</h3>
        <div className="field">
          <label>Initial portfolio ($)</label>
          <input type="number" value={params.init_portfolio} onChange={set("init_portfolio")} min={1} />
        </div>
        <div className="field">
          <label>Trade size (%)</label>
          <input type="number" value={params.trade_size_pct} onChange={set("trade_size_pct")} step={0.01} />
        </div>
        <div className="field">
          <label>Fee (%)</label>
          <input type="number" value={params.fee_pct} onChange={set("fee_pct")} step={0.0001} />
        </div>
        <div className="field">
          <label>Leverage</label>
          <input type="number" value={params.leverage} onChange={set("leverage")} min={1} />
        </div>
      </div>

      <button className="btn btn-primary" type="submit" disabled={loading || !params.filepath}>
        {loading ? "Running…" : "Run Backtest"}
      </button>
    </form>
  );
}
