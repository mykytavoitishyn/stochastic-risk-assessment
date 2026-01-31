import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns

rawdf = pd.read_csv("data/org/marketdata/BTCUSDT_5m_974764800000_1763683200000.csv")

sample_df = rawdf.head(1000).copy()

sample_df["log_return"] = np.log(sample_df["close_price"] / sample_df["close_price"].shift(1))

plt.figure(figsize=(12, 6))
plt.plot(sample_df["close_time"], sample_df["log_return"], label = "Log Return")
plt.xticks(sample_df["close_time"][::100], rotation=45)
plt.title("5m Close Price Returns")
plt.legend()
plt.tight_layout()
plt.show()

def manual_moving_average(series, window):
    """
    Calculate moving average manually
    
    Steps:
    1. Initialize empty list to store MA values
    2. Loop through the series
    3. For each position, take the last 'window' values
    4. Calculate the mean of those values
    5. Handle edge cases (not enough data at the start)
    """
    ma_values = []
    
    for i in range(len(series)):
        if i < window - 1:
            ma_values.append(np.nan)
        else:
            window_values = series.iloc[i - window + 1 : i + 1]
            
            mean_value = window_values.mean()
            
            ma_values.append(mean_value)
    
    return ma_values

sample_df["ma_200"] = manual_moving_average(sample_df["close_price"], window=200)
sample_df["ma_50"] = manual_moving_average(sample_df["close_price"], window=50)
sample_df["ma_21"] = manual_moving_average(sample_df["close_price"], window=21)


def manual_ema(series, window):
    """
    Calculate Exponential Moving Average manually
    
    Steps:
    1. Calculate smoothing factor (alpha)
    2. Initialize EMA with first valid value or SMA
    3. For each new value, apply EMA formula:
       EMA_t = alpha * Price_t + (1 - alpha) * EMA_{t-1}
    4. EMA gives more weight to recent prices
    """
    ema_values = []
    
    alpha = 2 / (window + 1)
    
    for i in range(len(series)):
        if i == 0:
            ema_values.append(series.iloc[i])
        else:
            current_price = series.iloc[i]
            previous_ema = ema_values[i - 1]
            
            current_ema = alpha * current_price + (1 - alpha) * previous_ema
            
            ema_values.append(current_ema)
    
    return ema_values

sample_df["ema_200"] = manual_moving_average(sample_df["close_price"], window=200)
sample_df["ema_50"] = manual_moving_average(sample_df["close_price"], window=50)
sample_df["ema_21"] = manual_moving_average(sample_df["close_price"], window=21)


plt.figure(figsize=(12, 6))
plt.plot(sample_df["close_time"], sample_df["close_price"], label="Close Price")
plt.plot(sample_df["close_time"], sample_df["ma_200"], label="MA 200")
plt.plot(sample_df["close_time"], sample_df["ma_50"], label="MA 50")
plt.plot(sample_df["close_time"], sample_df["ma_21"], label="MA 21")
plt.xticks(sample_df["close_time"][::100], rotation=45)
plt.title("MA 200, 50, 21 with close price")
plt.legend()
plt.tight_layout()
plt.show()


plt.figure(figsize=(12, 6))
plt.plot(sample_df["close_time"], sample_df["close_price"], label = "Close Price")
plt.plot(sample_df["close_time"], sample_df["ema_200"], label = "EMA 200")
plt.plot(sample_df["close_time"], sample_df["ema_50"], label = "EMA 50")
plt.plot(sample_df["close_time"], sample_df["ema_21"], label = "EMA 21")
plt.xticks(sample_df["close_time"][::100], rotation=45)
plt.title("EMA 200, 50, 21 with close price")
plt.legend()
plt.tight_layout()
plt.show()

def compute_atr(df, window=14):
    # True Range
    h_l = df["high_price"] - df["low_price"]
    h_pc = (df["high_price"] - df["close_price"].shift(1)).abs()
    l_pc = (df["low_price"] - df["close_price"].shift(1)).abs()

    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)

    # ATR (Wilder smoothing)
    atr = tr.ewm(alpha=1/window, adjust=False).mean()

    return atr


sample_df["ATR_14"] = compute_atr(sample_df, window = 14)

plt.figure(figsize=(12, 6))
plt.plot(sample_df["close_time"], sample_df["ATR_14"], label = "ATR 14")
plt.xticks(sample_df["close_time"][::100], rotation=45)
plt.title("Average True Range with window = 14")
plt.legend()
plt.tight_layout()
plt.show()

# trand long trends only
def generate_trend_pullback_signals(df):
    """
    Generates long-only entry signals based on:
    1. Uptrend confirmation (EMA50 > EMA200 and close > EMA200)
    2. Pullback (previous close < EMA21)
    3. Resume of trend (current close > EMA21)
    
    Returns df with a new column:
    - 'long_signal' = 1 when long entry condition triggers
                      0 otherwise
    """

    df = df.copy()

    df["trend_up"] = (df["close_price"] > df["ema_200"]) & (df["ema_50"] > df["ema_200"])

    df["pullback"] = df["close_price"].shift(1) < df["ema_21"].shift(1)

    df["resume"] = df["close_price"] > df["ema_21"]

    df["long_signal"] = (df["trend_up"] & df["pullback"] & df["resume"]).astype(int)

    return df

sample_df = generate_trend_pullback_signals(sample_df)
print(sample_df[["close_price", "ema_21", "ema_50", "ema_200", "long_signal"]].head(20))

plt.figure(figsize=(14, 6))
plt.plot(sample_df["close_time"], sample_df["close_price"], label="Close Price")
plt.plot(sample_df["close_time"], sample_df["ema_21"], label="EMA21")
plt.scatter(sample_df.loc[sample_df["long_signal"] == 1, "close_time"],
            sample_df.loc[sample_df["long_signal"] == 1, "close_price"],
            color="green", marker="^", label="Long Entry", s=80)
plt.legend()
plt.title("Pullback-to-EMA21 Trend Entries")
plt.xticks(sample_df["close_time"][::100], rotation=45)
plt.show()
