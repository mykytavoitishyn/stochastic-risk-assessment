import { useState } from 'react'
import axios from 'axios'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine,
} from 'recharts'

interface BacktestParams {
  symbol: string
  interval: string
  start_date: string
  end_date: string
  short_window: number
  long_window: number
  trend_window: number
  cross_persist: number
  rsi_buy: number
  rsi_sell: number
  use_vol_filter: boolean
  tp_pct: number
  sl_pct: number
  max_candles: number
  init_portfolio: number
  leverage: number
}

interface Summary {
  trades: number
  win_rate: number
  total_pnl: number
  final_portfolio: number
  avg_pnl: number
  best_trade: number
  worst_trade: number
  avg_candles: number
  sharpe: number
  max_drawdown: number
  exit_reasons: Record<string, number>
}

interface TradeRow {
  entry_time: string
  exit_time: string
  entry_price: number
  exit_price: number
  side: string
  candles: number
  exit_reason: string
  pnl: number
  portfolio: number
}

interface CurvePoint { time: string; portfolio: number }

const DEFAULTS: BacktestParams = {
  symbol: 'BTCUSDT', interval: '15m',
  start_date: '2025-01-01', end_date: '2026-03-21',
  short_window: 10, long_window: 20, trend_window: 100,
  cross_persist: 1, rsi_buy: 55, rsi_sell: 45,
  use_vol_filter: true, tp_pct: 0.05, sl_pct: 0.02,
  max_candles: 96, init_portfolio: 1000, leverage: 10,
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-slate-400">{label}</label>
      {children}
    </div>
  )
}

const inputCls = "bg-[#0f1117] border border-[#2a2d3e] rounded-lg px-3 py-1.5 text-sm text-white w-full focus:outline-none focus:border-indigo-500"

export function BacktestPanel() {
  const [params, setParams] = useState<BacktestParams>(DEFAULTS)
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<Summary | null>(null)
  const [trades, setTrades] = useState<TradeRow[]>([])
  const [curve, setCurve] = useState<CurvePoint[]>([])
  const [error, setError] = useState<string | null>(null)

  const set = (key: keyof BacktestParams, val: string | number | boolean) =>
    setParams(p => ({ ...p, [key]: val }))

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.post('/api/backtest/run', params)
      setSummary(data.summary)
      setTrades(data.trades)
      setCurve(data.portfolio_curve)
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message)
    } finally {
      setLoading(false)
    }
  }

  const pnlColor = (v: number) => v >= 0 ? 'text-emerald-400' : 'text-red-400'

  return (
    <div className="bg-[#1a1d2e] rounded-xl border border-[#2a2d3e] p-5">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-5">
        Backtest — MA Golden / Death Cross
      </h2>

      {/* Params */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <Field label="Symbol">
          <select className={inputCls} value={params.symbol} onChange={e => set('symbol', e.target.value)}>
            {['BTCUSDT','ETHUSDT','SOLUSDT','XRPUSDT','XAUUSDT'].map(s => <option key={s}>{s}</option>)}
          </select>
        </Field>
        <Field label="Interval">
          <select className={inputCls} value={params.interval} onChange={e => set('interval', e.target.value)}>
            {['15m','30m','1h','4h'].map(s => <option key={s}>{s}</option>)}
          </select>
        </Field>
        <Field label="Start date">
          <input className={inputCls} type="date" value={params.start_date} onChange={e => set('start_date', e.target.value)} />
        </Field>
        <Field label="End date">
          <input className={inputCls} type="date" value={params.end_date} onChange={e => set('end_date', e.target.value)} />
        </Field>

        <Field label="Short MA">
          <input className={inputCls} type="number" value={params.short_window} onChange={e => set('short_window', +e.target.value)} />
        </Field>
        <Field label="Long MA">
          <input className={inputCls} type="number" value={params.long_window} onChange={e => set('long_window', +e.target.value)} />
        </Field>
        <Field label="Trend MA">
          <input className={inputCls} type="number" value={params.trend_window} onChange={e => set('trend_window', +e.target.value)} />
        </Field>
        <Field label="Cross persist">
          <input className={inputCls} type="number" value={params.cross_persist} onChange={e => set('cross_persist', +e.target.value)} />
        </Field>

        <Field label="RSI buy ≤">
          <input className={inputCls} type="number" value={params.rsi_buy} onChange={e => set('rsi_buy', +e.target.value)} />
        </Field>
        <Field label="RSI sell ≥">
          <input className={inputCls} type="number" value={params.rsi_sell} onChange={e => set('rsi_sell', +e.target.value)} />
        </Field>
        <Field label="TP %">
          <input className={inputCls} type="number" step="0.01" value={params.tp_pct} onChange={e => set('tp_pct', +e.target.value)} />
        </Field>
        <Field label="SL %">
          <input className={inputCls} type="number" step="0.01" value={params.sl_pct} onChange={e => set('sl_pct', +e.target.value)} />
        </Field>

        <Field label="Portfolio $">
          <input className={inputCls} type="number" value={params.init_portfolio} onChange={e => set('init_portfolio', +e.target.value)} />
        </Field>
        <Field label="Leverage">
          <input className={inputCls} type="number" value={params.leverage} onChange={e => set('leverage', +e.target.value)} />
        </Field>
        <Field label="Vol filter">
          <select className={inputCls} value={String(params.use_vol_filter)} onChange={e => set('use_vol_filter', e.target.value === 'true')}>
            <option value="true">On</option>
            <option value="false">Off</option>
          </select>
        </Field>
        <Field label="Max candles">
          <input className={inputCls} type="number" value={params.max_candles} onChange={e => set('max_candles', +e.target.value)} />
        </Field>
      </div>

      <button
        onClick={run}
        disabled={loading}
        className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-white text-sm font-semibold transition-colors"
      >
        {loading ? 'Running...' : 'Run Backtest'}
      </button>

      {error && <p className="mt-3 text-red-400 text-sm">{error}</p>}

      {/* Results */}
      {summary && summary.trades > 0 && (
        <div className="mt-6 space-y-5">
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { label: 'Trades',       val: summary.trades },
              { label: 'Win rate',     val: `${summary.win_rate}%` },
              { label: 'Total PnL',    val: `$${summary.total_pnl.toFixed(2)}`, color: pnlColor(summary.total_pnl) },
              { label: 'Sharpe',       val: summary.sharpe, color: summary.sharpe > 0 ? 'text-emerald-400' : 'text-red-400' },
              { label: 'Max DD',       val: `${summary.max_drawdown}%`, color: 'text-red-400' },
              { label: 'Final portf.', val: `$${summary.final_portfolio.toFixed(0)}` },
              { label: 'Avg PnL',      val: `$${summary.avg_pnl.toFixed(2)}`, color: pnlColor(summary.avg_pnl) },
              { label: 'Best',         val: `$${summary.best_trade.toFixed(2)}`, color: 'text-emerald-400' },
              { label: 'Worst',        val: `$${summary.worst_trade.toFixed(2)}`, color: 'text-red-400' },
              { label: 'Avg hold',     val: `${summary.avg_candles} candles` },
            ].map(({ label, val, color }) => (
              <div key={label} className="bg-[#0f1117] rounded-lg p-3 border border-[#2a2d3e]">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <p className={`font-mono font-semibold text-sm ${color ?? 'text-white'}`}>{val}</p>
              </div>
            ))}
          </div>

          {/* Portfolio curve */}
          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wider">Portfolio Curve</p>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={curve} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 10 }} interval="preserveStartEnd"
                  tickFormatter={v => v.slice(0, 10)} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={v => `$${v}`} width={60} />
                <Tooltip
                  contentStyle={{ background: '#0f1117', border: '1px solid #2a2d3e', borderRadius: 8 }}
                  formatter={(v) => [`$${Number(v).toFixed(2)}`, 'Portfolio']}
                />
                <ReferenceLine y={params.init_portfolio} stroke="#64748b" strokeDasharray="4 4" />
                <Line type="monotone" dataKey="portfolio" stroke="#6366f1" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Trade table */}
          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wider">Trades ({trades.length})</p>
            <div className="overflow-x-auto max-h-64 overflow-y-auto">
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-[#1a1d2e]">
                  <tr className="text-slate-500 border-b border-[#2a2d3e]">
                    <th className="text-left pb-2">Entry</th>
                    <th className="text-left pb-2">Exit</th>
                    <th className="text-left pb-2">Side</th>
                    <th className="text-right pb-2">Entry $</th>
                    <th className="text-right pb-2">Exit $</th>
                    <th className="text-right pb-2">PnL</th>
                    <th className="text-right pb-2">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {[...trades].sort((a,b) => new Date(b.entry_time).getTime() - new Date(a.entry_time).getTime()).map((t, i) => (
                    <tr key={i} className="border-b border-[#2a2d3e] last:border-0 hover:bg-[#1f2235]">
                      <td className="py-1.5 text-slate-400">{t.entry_time.slice(0,16)}</td>
                      <td className="py-1.5 text-slate-400">{t.exit_time.slice(0,16)}</td>
                      <td className={`py-1.5 font-semibold ${t.side === 'BUY' ? 'text-emerald-400' : 'text-red-400'}`}>{t.side}</td>
                      <td className="py-1.5 text-right font-mono text-slate-200">${t.entry_price.toLocaleString()}</td>
                      <td className="py-1.5 text-right font-mono text-slate-200">${t.exit_price.toLocaleString()}</td>
                      <td className={`py-1.5 text-right font-mono font-semibold ${t.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {t.pnl >= 0 ? '+' : ''}${t.pnl.toFixed(2)}
                      </td>
                      <td className="py-1.5 text-right text-slate-500">{t.exit_reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {summary && summary.trades === 0 && (
        <p className="mt-4 text-slate-500 text-sm">No trades generated with these parameters.</p>
      )}
    </div>
  )
}
