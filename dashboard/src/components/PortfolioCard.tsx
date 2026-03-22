import type { Balance, Ticker } from '../api'

interface Props {
  balance: Balance | null
  ticker: Ticker | null
}

export function PortfolioCard({ balance, ticker }: Props) {
  const btcValue = balance && ticker
    ? balance.BTC.free * ticker.price
    : null
  const total = balance && btcValue !== null
    ? balance.USDT.free + btcValue
    : null

  return (
    <div className="bg-[#1a1d2e] rounded-xl p-5 border border-[#2a2d3e]">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Portfolio</h2>

      {balance ? (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-slate-300">USDT</span>
            <div className="text-right">
              <div className="text-white font-mono font-semibold">${balance.USDT.free.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
              {balance.USDT.locked > 0 && <div className="text-xs text-slate-500">locked: ${balance.USDT.locked.toFixed(2)}</div>}
            </div>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-slate-300">BTC</span>
            <div className="text-right">
              <div className="text-white font-mono font-semibold">{balance.BTC.free.toFixed(6)} BTC</div>
              {btcValue !== null && <div className="text-xs text-slate-500">≈ ${btcValue.toLocaleString('en-US', { maximumFractionDigits: 2 })}</div>}
              {balance.BTC.locked > 0 && <div className="text-xs text-slate-500">locked: {balance.BTC.locked.toFixed(6)}</div>}
            </div>
          </div>

          {total !== null && (
            <div className="border-t border-[#2a2d3e] pt-3 flex justify-between items-center">
              <span className="text-slate-400 text-sm">Total Value</span>
              <span className="text-emerald-400 font-mono font-bold text-lg">${total.toLocaleString('en-US', { maximumFractionDigits: 2 })}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="text-slate-500 text-sm">Loading...</div>
      )}
    </div>
  )
}
