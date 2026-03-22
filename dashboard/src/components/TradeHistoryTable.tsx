import type { Trade } from '../api'

interface Props { trades: Trade[] }

export function TradeHistoryTable({ trades }: Props) {
  const sorted = [...trades].sort((a, b) => b.time - a.time)

  return (
    <div className="bg-[#1a1d2e] rounded-xl p-5 border border-[#2a2d3e]">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
        Trade History <span className="ml-2 text-xs bg-[#2a2d3e] text-slate-300 px-2 py-0.5 rounded-full">{trades.length}</span>
      </h2>
      {trades.length === 0 ? (
        <p className="text-slate-500 text-sm">No trades yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs border-b border-[#2a2d3e]">
                <th className="text-left pb-2">Time</th>
                <th className="text-left pb-2">Side</th>
                <th className="text-right pb-2">Price</th>
                <th className="text-right pb-2">Qty</th>
                <th className="text-right pb-2">Total</th>
                <th className="text-right pb-2">Fee</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(t => (
                <tr key={t.id} className="border-b border-[#2a2d3e] last:border-0 hover:bg-[#1f2235] transition-colors">
                  <td className="py-2 text-slate-400 text-xs whitespace-nowrap">
                    {new Date(t.time).toLocaleString()}
                  </td>
                  <td className={`py-2 font-semibold ${t.isBuyer ? 'text-emerald-400' : 'text-red-400'}`}>
                    {t.isBuyer ? 'BUY' : 'SELL'}
                  </td>
                  <td className="py-2 text-right font-mono text-slate-200">${Number(t.price).toLocaleString()}</td>
                  <td className="py-2 text-right font-mono text-slate-200">{Number(t.qty).toFixed(6)}</td>
                  <td className="py-2 text-right font-mono text-slate-200">${Number(t.quoteQty).toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                  <td className="py-2 text-right text-slate-400 text-xs">{Number(t.commission).toFixed(6)} {t.commissionAsset}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
