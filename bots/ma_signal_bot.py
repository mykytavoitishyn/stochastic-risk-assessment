"""Signal bot: monitors BTC and sends buy/sell alerts to Discord."""
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BINANCE_URL = "https://api.binance.com"

symbol = "BTCUSDT"
interval = "1m"

check_interval_sec = 60


def get_klines(limit=100):
    """Fetch recent klines from Binance."""
    url = f"{BINANCE_URL}/api/v3/klines"
    resp = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": limit})
    resp.raise_for_status()
    return resp.json()

def send_discord(message):
    """Send message to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("No webhook configured")
        return False
    resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    return resp.status_code == 204


def main():
    last_signal = None
    while True:
        try:
            # Get data
            klines = get_klines(limit=50)
            closes = [float(k[4]) for k in klines]
            current_price = closes[-1]

            # Calculate RSI
            print("Successfully received the data.")
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] BTC: ${current_price:,.2f}", end="")

            signal = None
          
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(check_interval_sec)


if __name__ == "__main__":
    main()
