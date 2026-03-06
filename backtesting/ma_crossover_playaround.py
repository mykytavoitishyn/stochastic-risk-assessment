import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import os 
os.chdir("/home/mykyta/Code/personal/stochastic-risk-assessment")

# 15 min candles
data_path = "data/org/marketdata/BTCUSDT_15m_2000-11-21 00:00:00_2026-02-23 00:00:00.csv"

df = pd.read_csv(data_path, index_col=0)
df['open_time'] = pd.to_datetime(df['open_time'])

short_window = 20
long_window = 50
trend_window = 200
cross_persist = 2  # candles the cross must hold to avoid whipsaws

df = df.tail(2000)

# moving averages
df["ma_short"] = df["close_price"].rolling(window=short_window).mean()
df["ma_long"] = df["close_price"].rolling(window=long_window).mean()
df["ma_trend"] = df["close_price"].rolling(window=trend_window).mean()

# pct changes for price and volume
df["volume_change"] = df["quote_asset_volume"].pct_change()
df["price_change"] = df["close_price"].pct_change()

# RSI
rsi_window = 21
delta = df["close_price"].diff()
gain = delta.clip(lower=0) # take all the gains
loss = -delta.clip(upper=0) # take all the losses
avg_gain = gain.ewm(com=rsi_window - 1, min_periods=rsi_window).mean() # average gain across window
avg_loss = loss.ewm(com=rsi_window - 1, min_periods=rsi_window).mean() # average loss across window
rs = avg_gain / avg_loss # ratio gain over loss
df["rsi"] = 100 - (100 / (1 + rs)) # standardize from 0 to 100

# ATR
atr_window = 14
df["atr"] = (df["high_price"] - df["low_price"]).rolling(atr_window).mean()

df = df.dropna()

# ma crossover signals with persistence filter (avoids whipsaws)
df["cross_up"] = (df["ma_short"] > df["ma_long"]).astype(int)
df["cross_down"] = (df["ma_short"] < df["ma_long"]).astype(int)

df["signal"] = 0
buy_mask = (
    (df["cross_up"].rolling(cross_persist).min() == 1) # cross held n bars
    & (df["cross_up"].shift(cross_persist) == 0) # was below n bars ago (fresh cross)
    & (df["close_price"] > df["ma_trend"]) # trend filter
    # & (df["rsi"].shift(1) <= 50)  # rsi filter
)
sell_mask = (
    (df["cross_down"].rolling(cross_persist).min() == 1)
    & (df["cross_down"].shift(cross_persist) == 0)
    & (df["close_price"] < df["ma_trend"])
    # & (df["rsi"].shift(1) >= 50)
)
df.loc[buy_mask, "signal"] = 1
df.loc[sell_mask, "signal"] = -1


# aggressive simulation
def simulate_trades(df, init_portfolio=1_000, trade_size_pct=0.05,
                    fee_pct=0.0005, leverage=20,
                    sl_atr_mult = 1.5, tp_atr_mult=3.0):
    margin   = init_portfolio * trade_size_pct
    notional = margin * leverage

    signal_idx = df[df["signal"] != 0].index.tolist()
    trades = []

    for i, idx in enumerate(signal_idx):
        row       = df.loc[idx]
        direction = row["signal"]
        entry     = row["close_price"]
        atr       = row["atr"]

        sl = entry - direction * sl_atr_mult * atr
        tp = entry + direction * tp_atr_mult * atr

        end_idx       = signal_idx[i + 1] if i + 1 < len(signal_idx) else df.index[-1]
        trade_candles = df.loc[idx:end_idx]

        exit_price  = trade_candles.iloc[-1]["close_price"]
        exit_time   = trade_candles.iloc[-1]["open_time"]
        exit_reason = "signal"
        candles_passed = len(trade_candles) - 1

        for j, (_, c) in enumerate(trade_candles.iterrows()):
            if direction == 1:  # long: stopped below sl, took profit above tp
                if c["low_price"] <= sl:
                    exit_price, exit_time, exit_reason, candles_passed = sl, c["open_time"], "sl", j
                    break
                if c["high_price"] >= tp:
                    exit_price, exit_time, exit_reason, candles_passed = tp, c["open_time"], "tp", j
                    break
            else:               # short: stopped above sl, took profit below tp
                if c["high_price"] >= sl:
                    exit_price, exit_time, exit_reason, candles_passed = sl, c["open_time"], "sl", j
                    break
                if c["low_price"] <= tp:
                    exit_price, exit_time, exit_reason, candles_passed = tp, c["open_time"], "tp", j
                    break

        ret = direction * (exit_price - entry) / entry
        pnl = (ret * notional) - notional * fee_pct * 2

        trades.append({
            "entry_time":     row["open_time"],
            "exit_time":      exit_time,
            "entry_price":    entry,
            "exit_price":     exit_price,
            "signal":         direction,
            "ret":            ret,
            "pnl":            pnl,
            "exit_reason":    exit_reason,
            "candles":        candles_passed,
            "time_held":      exit_time - row["open_time"],
        })

    t = pd.DataFrame(trades)
    t["portfolio"] = init_portfolio + t["pnl"].cumsum()
    return t


trades = simulate_trades(df)
if not trades.empty:
    total_pnl = trades["pnl"].sum()
    win_rate  = (trades["pnl"] > 0).mean()
    by_reason = trades["exit_reason"].value_counts()
    print(f"Trades: {len(trades)} | Total PnL: ${total_pnl:.2f} | Win rate: {win_rate:.1%} | Final portfolio: ${trades['portfolio'].iloc[-1]:.2f}")
    print(f"Exits  — SL: {by_reason.get('sl', 0)} | TP: {by_reason.get('tp', 0)} | Signal: {by_reason.get('signal', 0)}")
    print(trades[["entry_time", "exit_time", "entry_price", "exit_price", "signal", "ret", "pnl", "exit_reason", "candles", "time_held"]].to_string(index=False))


# plot ma's

fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1, figsize=(12, 8))

# plot 1
ax1.plot(df["open_time"], df["close_price"], alpha = 1, label = "BTC/USDT")
ax1.plot(df["open_time"], df["ma_short"], alpha = 0.7, label = "MA-short")
ax1.plot(df["open_time"], df["ma_long"], alpha = 0.7, label = "MA-long")
ax1.plot(df["open_time"], df["ma_trend"], alpha = 0.7, label = "MA-trend")

ax1.vlines(df.loc[df['signal'] == 1, "open_time"], ymin = df["close_price"].min(), ymax=df["close_price"].max(), colors="green", alpha = 0.5, label="Buy signal")
ax1.vlines(df.loc[df['signal'] == -1, "open_time"], ymin = df["close_price"].min(), ymax=df["close_price"].max(), colors="red", alpha = 0.5, label="Buy signal")

ax1.grid(True, alpha=0.3)
ax1.set_title("MA's 20/50/200 BTC/USDT 15-min candle")
handles1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(handles1, labels1, fontsize = 10)

# plot 2
ax2.plot(df["open_time"], df["volume_change"], alpha = 1, label = "Quote asset volume change(%)")

ax2.grid(True, alpha = 0.3)
handles2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(handles2, labels2, fontsize = 10)
ax2.set_title("BTC/USDT 15-min quote asset volume change in %")

# plot3
ax3.plot(df["open_time"], df["price_change"], alpha = 1, label = "Close price change(%)", color = "purple")

ax3.grid(True, alpha = 0.3)
handles3, labels3 = ax3.get_legend_handles_labels()
ax3.legend(handles3, labels3, fontsize = 10)
ax3.set_title("BTC/USDT close price change in %")


# plot 4
ax4.plot(df["open_time"], df["rsi"], alpha=1, label="RSI-14", color="orange")
ax4.axhline(60, linestyle="--", color="red", alpha=0.3, label="Overbought (70)")
ax4.axhline(40, linestyle="--", color="green", alpha=0.3, label="Oversold (30)")

ax4.grid(True, alpha=0.3)
handles4, labels4 = ax4.get_legend_handles_labels()
ax4.legend(handles4, labels4, fontsize=10)
ax4.set_title("RSI-14")

date_fmt = mdates.DateFormatter("%b %d")
for ax in (ax1, ax2, ax3, ax4):
    ax.xaxis.set_major_formatter(date_fmt)

plt.show()


