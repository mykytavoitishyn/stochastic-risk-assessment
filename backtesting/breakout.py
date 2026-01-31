import pandas as pd


def breakout_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    lookback_period: int = 20,
    breakout_threshold: float = 0.01,
) -> dict:
    """
    Breakout strategy: buy on resistance breakout, sell on support breakdown.

    Parameters:
        df: DataFrame with OHLCV data
        initial_capital: Starting capital in USDT
        lookback_period: Periods to calculate support/resistance
        breakout_threshold: % above/below S/R to confirm breakout

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    df['resistance'] = df['high_price'].rolling(window=lookback_period).max()
    df['support'] = df['low_price'].rolling(window=lookback_period).min()
    df['resistance_breakout'] = df['resistance'] * (1 + breakout_threshold)
    df['support_breakdown'] = df['support'] * (1 - breakout_threshold)
    df['prev_close'] = df['close_price'].shift(1)

    df['buy_signal'] = (df['close_price'] > df['resistance_breakout']) & \
                       (df['prev_close'] <= df['resistance'].shift(1))
    df['sell_signal'] = (df['close_price'] < df['support_breakdown']) & \
                        (df['prev_close'] >= df['support'].shift(1))

    cash = initial_capital
    btc_holdings = 0.0
    df['portfolio_value'] = 0.0

    start_idx = lookback_period + 1
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        price = row['close_price']

        if row['buy_signal'] and btc_holdings == 0:
            btc_holdings = cash / price
            cash = 0.0
        elif row['sell_signal'] and btc_holdings > 0:
            cash = btc_holdings * price
            btc_holdings = 0.0

        df.at[idx, 'portfolio_value'] = cash + (btc_holdings * price)

    df.loc[:start_idx, 'portfolio_value'] = initial_capital

    return {
        'strategy': f'Breakout ({lookback_period}d, {breakout_threshold*100:.0f}%)',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
