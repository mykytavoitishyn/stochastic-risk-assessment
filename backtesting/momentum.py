import pandas as pd


def momentum_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    lookback_period: int = 10,
    momentum_threshold: float = 0.05,
) -> dict:
    """
    Momentum strategy: buy when momentum > threshold, sell when momentum < 0.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        initial_capital: Starting capital in USDT
        lookback_period: Period to calculate momentum (rate of change)
        momentum_threshold: Minimum momentum % to enter position

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    df['momentum'] = df['close_price'].pct_change(periods=lookback_period)
    df['buy_signal'] = df['momentum'] > momentum_threshold
    df['sell_signal'] = df['momentum'] < 0

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
        'strategy': f'Momentum ({lookback_period}d, >{momentum_threshold*100:.0f}%)',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
