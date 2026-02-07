"""Fetch BTC price from Binance every 5 minutes and send to Discord."""
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BINANCE_BASE_URL = "https://api.binance.com"
SYMBOL = "BTCUSDT"
INTERVAL_SECONDS = 5 * 60  # 5 minutes


def get_btc_price() -> dict:
    """Fetch current BTC price from Binance."""
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": SYMBOL})
    response.raise_for_status()
    data = response.json()
    return float(data["price"])


def send_discord_message(content: str) -> bool:
    """Send message to Discord via webhook."""
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL not set in .env")
        return False

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": content}
    )
    return response.status_code == 204


def main():
    print(f"Starting BTC price tracker...")
    print(f"Interval: {INTERVAL_SECONDS // 60} minutes")
    print(f"Discord webhook: {'configured' if DISCORD_WEBHOOK_URL else 'NOT SET'}")
    print("-" * 40)

    while True:
        try:
            price = get_btc_price()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = f"**BTC/USDT** ${price:,.2f} | {timestamp}"

            print(f"[{timestamp}] BTC: ${price:,.2f}")

            if send_discord_message(message):
                print("  -> Sent to Discord")
            else:
                print("  -> Failed to send to Discord")

        except requests.RequestException as e:
            print(f"Error fetching price: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
