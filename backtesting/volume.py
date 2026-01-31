import pandas as pd


def volume_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    volume_ma_period: int = 20,
    volume_spike_threshold: float = 2.0,
    exit_days: int = 5,
) -> dict:
    """
    Volume spike strategy: buy on high volume + green candle, exit after N days.

    Parameters:
        df: DataFrame with OHLCV data
        initial_capital: Starting capital in USDT
        volume_ma_period: Period for volume moving average
        volume_spike_threshold: Buy when volume is this multiple of average
        exit_days: Exit position after this many days

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    df['volume_ma'] = df['volume'].rolling(window=volume_ma_period).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    df['volume_spike'] = (df['volume'] > df['volume_ma'] * volume_spike_threshold) & \
                         (df['close_price'] > df['open_price'])

    cash = initial_capital
    btc_holdings = 0.0
    entry_day = None
    df['portfolio_value'] = 0.0

    start_idx = volume_ma_period
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        price = row['close_price']

        # Exit check
        if btc_holdings > 0:
            days_held = idx - entry_day
            should_exit = (days_held >= exit_days) or (row['volume_ratio'] < 1.0)
            if should_exit:
                cash = btc_holdings * price
                btc_holdings = 0.0
                entry_day = None

        # Entry check
        if row['volume_spike'] and btc_holdings == 0:
            btc_holdings = cash / price
            cash = 0.0
            entry_day = idx

        df.at[idx, 'portfolio_value'] = cash + (btc_holdings * price)

    df.loc[:start_idx, 'portfolio_value'] = initial_capital

    return {
        'strategy': f'Volume Spike ({volume_spike_threshold}x, {exit_days}d hold)',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
