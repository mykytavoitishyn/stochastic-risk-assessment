import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root)
sys.path.insert(0, root)

import os
from dotenv import load_dotenv
from src.marketdata import send_market_buy_order, send_market_sell_order

load_dotenv()

API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")
BASE_URL = "https://testnet.binance.vision"

buy_result = send_market_buy_order(
    api_key=API_KEY,
    api_secret=API_SECRET,
    symbol="BTCUSDT",
    quantity=0.001,
    base_url=BASE_URL,
)
print("BUY:", buy_result)

sell_result = send_market_sell_order(
    api_key=API_KEY,
    api_secret=API_SECRET,
    symbol="BTCUSDT",
    quantity=0.1,
    base_url=BASE_URL,
)
print("SELL:", sell_result)
