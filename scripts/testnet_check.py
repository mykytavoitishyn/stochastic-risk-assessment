import os, sys
root = "/home/mykyta/Code/personal/stochastic-risk-assessment"
os.chdir(root)
sys.path.insert(0, root)

from dotenv import load_dotenv
from src.marketdata import ping_binance, get_balance, send_market_buy_order, send_market_sell_order

load_dotenv()

API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")
BASE_URL = "https://testnet.binance.vision"
SYMBOL = "BTCUSDT"
QTY = 0.001

# 1. Ping
print("=== Testnet Connection ===")
ok = ping_binance(BASE_URL)
print(f"Ping: {'OK' if ok else 'FAILED'}")
if not ok:
    sys.exit(1)

# 2. Starting balances
print("\n=== Starting Balances ===")
usdt = get_balance(API_KEY, API_SECRET, asset="USDT", base_url=BASE_URL)
btc  = get_balance(API_KEY, API_SECRET, asset="BTC",  base_url=BASE_URL)
print(f"USDT: {usdt['free']:,.2f} (locked: {usdt['locked']:,.2f})")
print(f"BTC:  {btc['free']:.6f}  (locked: {btc['locked']:.6f})")

# 3. Buy
print(f"\n=== BUY {QTY} BTC ===")
buy = send_market_buy_order(API_KEY, API_SECRET, symbol=SYMBOL, quantity=QTY, base_url=BASE_URL)
print(f"Order ID: {buy['orderId']} | Status: {buy['status']} | Filled: {buy['executedQty']} BTC")

# 4. Balance after buy
print("\n=== Balances After Buy ===")
usdt = get_balance(API_KEY, API_SECRET, asset="USDT", base_url=BASE_URL)
btc  = get_balance(API_KEY, API_SECRET, asset="BTC",  base_url=BASE_URL)
print(f"USDT: {usdt['free']:,.2f}")
print(f"BTC:  {btc['free']:.6f}")

# 5. Sell
print(f"\n=== SELL {QTY} BTC ===")
sell = send_market_sell_order(API_KEY, API_SECRET, symbol=SYMBOL, quantity=QTY, base_url=BASE_URL)
print(f"Order ID: {sell['orderId']} | Status: {sell['status']} | Filled: {sell['executedQty']} BTC")

# 6. Final balances
print("\n=== Final Balances ===")
usdt = get_balance(API_KEY, API_SECRET, asset="USDT", base_url=BASE_URL)
btc  = get_balance(API_KEY, API_SECRET, asset="BTC",  base_url=BASE_URL)
print(f"USDT: {usdt['free']:,.2f}")
print(f"BTC:  {btc['free']:.6f}")

print("\nDone.")
