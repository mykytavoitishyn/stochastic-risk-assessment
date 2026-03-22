import axios from 'axios'

export interface AssetBalance { free: number; locked: number }
export interface Balance { USDT: AssetBalance; BTC: AssetBalance }

export interface OpenOrder {
  orderId: number
  symbol: string
  side: string
  type: string
  origQty: string
  price: string
  time: number
  status: string
}

export interface Trade {
  id: number
  orderId: number
  symbol: string
  side: 'BUY' | 'SELL' | string  // isBuyer from Binance
  isBuyer: boolean
  price: string
  qty: string
  quoteQty: string
  commission: string
  commissionAsset: string
  time: number
}

export interface Ticker {
  symbol: string
  price: number
  price_change_pct: number
  high: number
  low: number
  volume: number
  quote_volume: number
  trades: number
}

export interface Candle {
  open_time: string
  open_price: number
  high_price: number
  low_price: number
  close_price: number
  volume: number
}

export const fetchBalance   = () => axios.get<Balance>('/api/balance').then(r => r.data)
export const fetchOpenOrders = (symbol = 'BTCUSDT') => axios.get<OpenOrder[]>(`/api/open-orders?symbol=${symbol}`).then(r => r.data)
export const fetchTrades     = (symbol = 'BTCUSDT') => axios.get<Trade[]>(`/api/trades?symbol=${symbol}`).then(r => r.data)
export const fetchTicker     = (symbol = 'BTCUSDT') => axios.get<Ticker>(`/api/ticker?symbol=${symbol}`).then(r => r.data)
export const fetchKlines     = (symbol = 'BTCUSDT', interval = '15m') => axios.get<Candle[]>(`/api/klines?symbol=${symbol}&interval=${interval}`).then(r => r.data)
