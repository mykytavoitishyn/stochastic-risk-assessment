import type { OpenOrder } from '../api'

interface Props { orders: OpenOrder[] }

export function OpenOrdersTable({ orders }: Props) {
  return (
    <div className="bg-[#1a1d2e] rounded-xl p-5 border border-[#2a2d3e]">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
        Open Orders <span className="ml-2 text-xs bg-[#2a2d3e] text-slate-300 px-2 py-0.5 rounded-full">{orders.length}</span>
      </h2>
      {orders.length === 0 ? (
        <p className="text-slate-500 text-sm">No open orders</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs border-b border-[#2a2d3e]">
                <th className="text-left pb-2">Side</th>
                <th className="text-right pb-2">Price</th>
                <th className="text-right pb-2">Qty</th>
                <th className="text-right pb-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.orderId} className="border-b border-[#2a2d3e] last:border-0">
                  <td className={`py-2 font-semibold ${o.side === 'BUY' ? 'text-emerald-400' : 'text-red-400'}`}>{o.side}</td>
                  <td className="py-2 text-right font-mono text-slate-200">${Number(o.price).toLocaleString()}</td>
                  <td className="py-2 text-right font-mono text-slate-200">{Number(o.origQty).toFixed(6)}</td>
                  <td className="py-2 text-right text-slate-400 text-xs">{new Date(o.time).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
