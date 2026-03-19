import { useState, useEffect } from "react";

const defaults = {
  filepath: "",
  start_date: "2026-01-01",
  end_date: "2026-03-01",
  short_windows: "10,20,30",
  long_windows: "50,70,100",
  trend_windows: "100,200",
  cross_persist: "1,2,3,4",
  trade_size_pcts: "0.02,0.05,0.1",
  rsi_buy: 55,
  rsi_sell: 45,
  rsi_window: 14,
  fee_pct: 0.0005,
  leverage: 1,
  init_portfolio: 1000,
};

const parseList = (s, float = false) =>
  s.split(",").map((v) => (float ? parseFloat(v.trim()) : parseInt(v.trim(), 10))).filter((v) => !isNaN(v));

export default function GridSearchForm({ onRun, loading }) {
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

  const combinations =
    parseList(params.short_windows).length *
    parseList(params.long_windows).length *
    parseList(params.trend_windows).length *
    parseList(params.cross_persist).length *
    parseList(params.trade_size_pcts, true).length;

  const handleSubmit = (e) => {
    e.preventDefault();
    onRun({
      filepath: params.filepath,
      start_date: params.start_date,
      end_date: params.end_date,
      short_windows: parseList(params.short_windows),
      long_windows: parseList(params.long_windows),
      trend_windows: parseList(params.trend_windows),
      cross_persist: parseList(params.cross_persist),
      trade_size_pcts: parseList(params.trade_size_pcts, true),
      rsi_buy: +params.rsi_buy,
      rsi_sell: +params.rsi_sell,
      rsi_window: +params.rsi_window,
      fee_pct: +params.fee_pct,
      leverage: +params.leverage,
      init_portfolio: +params.init_portfolio,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-section">
        <h3>Data</h3>
        <div className="field">
          <label>File</label>
          <select value={params.filepath} onChange={set("filepath")}>
            {files.map((f) => <option key={f} value={f}>{f.split("/").pop()}</option>)}
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
        <h3>Search Space (comma-separated)</h3>
        <div className="field">
          <label>Short windows</label>
          <input value={params.short_windows} onChange={set("short_windows")} />
        </div>
        <div className="field">
          <label>Long windows</label>
          <input value={params.long_windows} onChange={set("long_windows")} />
        </div>
        <div className="field">
          <label>Trend windows</label>
          <input value={params.trend_windows} onChange={set("trend_windows")} />
        </div>
        <div className="field">
          <label>Cross persist</label>
          <input value={params.cross_persist} onChange={set("cross_persist")} />
        </div>
        <div className="field">
          <label>Trade size %</label>
          <input value={params.trade_size_pcts} onChange={set("trade_size_pcts")} />
        </div>
      </div>

      <div className="form-section">
        <h3>Fixed Params</h3>
        <div className="field">
          <label>RSI window</label>
          <input type="number" value={params.rsi_window} onChange={set("rsi_window")} />
        </div>
        <div className="field">
          <label>RSI buy / sell</label>
          <div style={{ display: "flex", gap: 6 }}>
            <input type="number" value={params.rsi_buy} onChange={set("rsi_buy")} />
            <input type="number" value={params.rsi_sell} onChange={set("rsi_sell")} />
          </div>
        </div>
        <div className="field">
          <label>Fee %</label>
          <input type="number" value={params.fee_pct} onChange={set("fee_pct")} step={0.0001} />
        </div>
        <div className="field">
          <label>Leverage</label>
          <input type="number" value={params.leverage} onChange={set("leverage")} min={1} />
        </div>
        <div className="field">
          <label>Initial portfolio ($)</label>
          <input type="number" value={params.init_portfolio} onChange={set("init_portfolio")} />
        </div>
      </div>

      <div style={{ color: "#8b949e", fontSize: 11, marginBottom: 10 }}>
        {combinations} combinations
      </div>

      <button className="btn btn-primary" type="submit" disabled={loading || !params.filepath}>
        {loading ? "Searching…" : "Run Grid Search"}
      </button>
    </form>
  );
}
