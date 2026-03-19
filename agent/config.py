BINANCE_BASE_URL = "https://api.binance.com"
MODEL = "claude-sonnet-4-6"
DEFAULT_CANDLES = 96   # 24h of 15m candles
MA_PERIOD = 200

SYSTEM = (
    "You are a real-time BTC/USDT market analyst. "
    "Be concise. Round prices to 2 decimal places. Express volatility as a percentage."
)
