import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BINANCE_BASE_URL = "https://api.binance.com"
SYMBOL = "BTCUSDT"
INTERVAL_SECONDS = 60


def get_btc_price() -> float:
    """Fetch current BTC price from Binance."""
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": SYMBOL})
    response.raise_for_status()
    data = response.json()
    return float(data["price"])


def get_volume_overview() -> dict:
    """Fetch 24h volume stats for BTC from Binance."""
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"
    response = requests.get(url, params={"symbol": SYMBOL})
    response.raise_for_status()
    data = response.json()
    return {
        "volume": float(data["volume"]),  # BTC traded
        "quote_volume": float(data["quoteVolume"]),  # USDT traded
        "price_change_pct": float(data["priceChangePercent"]),
        "high": float(data["highPrice"]),
        "low": float(data["lowPrice"]),
        "trades": int(data["count"]),
    }


def send_discord_message(content: str) -> bool:
    """Send message to Discord via webhook."""
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL not set in .env")
        return False

    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    return response.status_code == 204


def main():
    while True:
        try:
            price = get_btc_price()
            vol = get_volume_overview()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = (
                f"**BTC/USDT** ${price:,.2f} | {timestamp}\n"
                f"24h Change: {vol['price_change_pct']:+.2f}% | "
                f"High: ${vol['high']:,.2f} | Low: ${vol['low']:,.2f}\n"
                f"Volume: {vol['volume']:,.2f} BTC (${vol['quote_volume'] / 1e6:,.1f}M) | "
                f"Trades: {vol['trades']:,}"
            )

            print(f"[{timestamp}] BTC: ${price:,.2f}")

            if send_discord_message(message):
                print("Sent to Discord")
            else:
                print("Failed to send to Discord")

        except requests.RequestException as e:
            print(f"Error fetching price: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
