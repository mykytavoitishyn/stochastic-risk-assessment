import type { Candle } from '../api'
import {
  ComposedChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Area,
} from 'recharts'

interface Props { candles: Candle[] }

export function PriceChart({ candles }: Props) {
  if (!candles.length) return <div className="h-72 bg-[#1a1d2e] rounded-xl animate-pulse" />

  const data = candles.map(c => ({
    ...c,
    time: c.open_time.slice(11, 16),
  }))

  const prices = data.map(d => d.close_price)
  const minP = Math.min(...prices)
  const maxP = Math.max(...prices)
  const pad  = (maxP - minP) * 0.05

  return (
    <div className="bg-[#1a1d2e] rounded-xl p-4 border border-[#2a2d3e]">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Price Chart (15m)</h2>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
          <defs>
            <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
          <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis
            domain={[minP - pad, maxP + pad]}
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickFormatter={(v: number) => `$${v.toLocaleString()}`}
            width={80}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload[0]?.payload as Candle & { time: string }
              const up = d.close_price >= d.open_price
              return (
                <div className="bg-[#0f1117] border border-[#2a2d3e] rounded-lg p-3 text-xs font-mono">
                  <p className="text-slate-400 mb-1">{d.open_time?.slice(0, 16)}</p>
                  <p className="text-slate-300">O: <span className="text-white">${d.open_price?.toLocaleString()}</span></p>
                  <p className="text-emerald-400">H: ${d.high_price?.toLocaleString()}</p>
                  <p className="text-red-400">L: ${d.low_price?.toLocaleString()}</p>
                  <p className={up ? 'text-emerald-400' : 'text-red-400'}>C: ${d.close_price?.toLocaleString()}</p>
                  <p className="text-slate-400">Vol: {Number(d.volume).toFixed(2)}</p>
                </div>
              )
            }}
          />
          <Area
            type="monotone"
            dataKey="close_price"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#priceGrad)"
            dot={false}
          />
          <Line type="monotone" dataKey="high_price" stroke="#10b981" dot={false} strokeWidth={1} strokeDasharray="3 3" />
          <Line type="monotone" dataKey="low_price"  stroke="#ef4444" dot={false} strokeWidth={1} strokeDasharray="3 3" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
