import type { Ticker } from '../api'

interface Props { ticker: Ticker | null }

export function TickerBar({ ticker }: Props) {
  if (!ticker) return <div className="h-12 bg-[#1a1d2e] rounded-xl animate-pulse mb-4" />

  const up = ticker.price_change_pct >= 0
  return (
    <div className="bg-[#1a1d2e] rounded-xl px-6 py-3 border border-[#2a2d3e] flex flex-wrap gap-6 items-center">
      <div>
        <span className="text-slate-400 text-sm mr-2">{ticker.symbol}</span>
        <span className="text-white font-mono font-bold text-xl">${ticker.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
        <span className={`ml-3 font-mono text-sm font-semibold ${up ? 'text-emerald-400' : 'text-red-400'}`}>
          {up ? '+' : ''}{ticker.price_change_pct.toFixed(2)}%
        </span>
      </div>
      <div className="flex gap-5 text-sm text-slate-400">
        <span>H: <span className="text-slate-200">${ticker.high.toLocaleString()}</span></span>
        <span>L: <span className="text-slate-200">${ticker.low.toLocaleString()}</span></span>
        <span>Vol: <span className="text-slate-200">{ticker.volume.toLocaleString('en-US', { maximumFractionDigits: 1 })} BTC</span></span>
        <span>Trades: <span className="text-slate-200">{ticker.trades.toLocaleString()}</span></span>
      </div>
    </div>
  )
}
