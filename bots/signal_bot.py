"""Signal bot: monitors BTC and sends buy/sell alerts to Discord."""
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BINANCE_URL = "https://api.binance.com"
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
CHECK_INTERVAL = 60


def get_klines(limit=100):
    """Fetch recent klines from Binance."""
    url = f"{BINANCE_URL}/api/v3/klines"
    resp = requests.get(url, params={"symbol": SYMBOL, "interval": INTERVAL, "limit": limit})
    resp.raise_for_status()
    return resp.json()


def calculate_rsi(closes, period=14):
    """Calculate RSI from close prices."""
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]

    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def send_discord(message):
    """Send message to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("No webhook configured")
        return False
    resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    return resp.status_code == 204


def main():
    print("=" * 50)
    print("  BTC Signal Bot Started")
    print("=" * 50)
    print(f"Strategy: RSI ({RSI_PERIOD}) | Buy < {RSI_OVERSOLD} | Sell > {RSI_OVERBOUGHT}")
    print(f"Checking every {CHECK_INTERVAL} seconds")
    print("-" * 50)

    last_signal = None  # Track last signal to avoid spam

    while True:
        try:
            # Get data
            klines = get_klines(limit=50)
            closes = [float(k[4]) for k in klines]
            current_price = closes[-1]

            # Calculate RSI
            rsi = calculate_rsi(closes, RSI_PERIOD)

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] BTC: ${current_price:,.2f} | RSI: {rsi:.1f}", end="")

            # Check for signals
            signal = None
            if rsi < RSI_OVERSOLD and last_signal != "BUY":
                signal = "BUY"
                msg = (
                    f"🟢 **BUY SIGNAL**\n"
                    f"```\n"
                    f"Price:  ${current_price:,.2f}\n"
                    f"RSI:    {rsi:.1f} (oversold < {RSI_OVERSOLD})\n"
                    f"Time:   {timestamp}\n"
                    f"```"
                )
                send_discord(msg)
                last_signal = "BUY"
                print(f" -> 🟢 BUY SIGNAL SENT!")

            elif rsi > RSI_OVERBOUGHT and last_signal != "SELL":
                signal = "SELL"
                msg = (
                    f"🔴 **SELL SIGNAL**\n"
                    f"```\n"
                    f"Price:  ${current_price:,.2f}\n"
                    f"RSI:    {rsi:.1f} (overbought > {RSI_OVERBOUGHT})\n"
                    f"Time:   {timestamp}\n"
                    f"```"
                )
                send_discord(msg)
                last_signal = "SELL"
                print(f" -> 🔴 SELL SIGNAL SENT!")
            else:
                # No signal - send status update
                msg = (
                    f"⚪ **No Signal**\n"
                    f"```\n"
                    f"Price:  ${current_price:,.2f}\n"
                    f"RSI:    {rsi:.1f} (neutral: {RSI_OVERSOLD}-{RSI_OVERBOUGHT})\n"
                    f"Time:   {timestamp}\n"
                    f"```"
                )
                send_discord(msg)
                print(f" -> ⚪ Status sent")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
