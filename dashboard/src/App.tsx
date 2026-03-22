import { useEffect, useState, useCallback } from 'react'
import {
  fetchBalance, fetchOpenOrders, fetchTrades, fetchTicker, fetchKlines,
} from './api'
import type { Balance, OpenOrder, Trade, Ticker, Candle } from './api'
import { PortfolioCard } from './components/PortfolioCard'
import { TickerBar } from './components/TickerBar'
import { PriceChart } from './components/PriceChart'
import { OpenOrdersTable } from './components/OpenOrdersTable'
import { TradeHistoryTable } from './components/TradeHistoryTable'
import { BacktestPanel } from './components/BacktestPanel'
import './index.css'

const REFRESH_MS = 10_000

export default function App() {
  const [balance, setBalance]     = useState<Balance | null>(null)
  const [orders, setOrders]       = useState<OpenOrder[]>([])
  const [trades, setTrades]       = useState<Trade[]>([])
  const [ticker, setTicker]       = useState<Ticker | null>(null)
  const [candles, setCandles]     = useState<Candle[]>([])
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [error, setError]         = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const [bal, ord, trd, tick, kl] = await Promise.all([
        fetchBalance(),
        fetchOpenOrders(),
        fetchTrades(),
        fetchTicker(),
        fetchKlines(),
      ])
      setBalance(bal)
      setOrders(ord)
      setTrades(trd)
      setTicker(tick)
      setCandles(kl)
      setLastUpdate(new Date())
      setError(null)
    } catch (e: any) {
      setError(e?.message ?? 'Failed to fetch data')
    }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, REFRESH_MS)
    return () => clearInterval(id)
  }, [refresh])

  return (
    <div className="min-h-screen bg-[#0f1117] text-slate-200 p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-bold text-white tracking-tight">Trading Dashboard <span className="text-slate-500 font-normal text-sm ml-1">testnet</span></h1>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          {error && <span className="text-red-400">{error}</span>}
          {lastUpdate && <span>Updated {lastUpdate.toLocaleTimeString()}</span>}
          <button onClick={refresh} className="px-3 py-1 bg-[#2a2d3e] hover:bg-[#353848] rounded-lg text-slate-300 transition-colors">
            Refresh
          </button>
        </div>
      </div>

      {/* Ticker */}
      <div className="mb-4">
        <TickerBar ticker={ticker} />
      </div>

      {/* Chart */}
      <div className="mb-4">
        <PriceChart candles={candles} />
      </div>

      {/* Portfolio + Open Orders */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <PortfolioCard balance={balance} ticker={ticker} />
        <OpenOrdersTable orders={orders} />
      </div>

      {/* Trade History */}
      <div className="mb-4">
        <TradeHistoryTable trades={trades} />
      </div>

      {/* Backtest */}
      <BacktestPanel />
    </div>
  )
}
