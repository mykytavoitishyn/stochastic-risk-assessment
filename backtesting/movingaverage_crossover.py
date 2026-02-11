import pandas as pd


def ma_crossover_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    short_window: int = 50,
    long_window: int = 200,
) -> dict:
    """
    MA Crossover strategy: buy on golden cross, sell on death cross.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        initial_capital: Starting capital in USDT
        short_window: Short MA period
        long_window: Long MA period

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    # two moving averages
    df['ma_short'] = df['close_price'].rolling(window=short_window).mean()
    df['ma_long'] = df['close_price'].rolling(window=long_window).mean()

    df['signal'] = 0
    df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1
    df.loc[df['ma_short'] <= df['ma_long'], 'signal'] = -1
    df['crossover'] = df['signal'] - df['signal'].shift(1)

    # initialization
    cash = initial_capital
    btc_holdings = 0.0
    df['portfolio_value'] = 0.0

    start_idx = long_window
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        price = row['close_price']

        if row['crossover'] == 2 and btc_holdings == 0:  # Golden cross
            btc_holdings = cash / price # buy
            cash = 0.0
        elif row['crossover'] == -2 and btc_holdings > 0:  # Death cross
            cash = btc_holdings * price # sell
            btc_holdings = 0.0

        df.at[idx, 'portfolio_value'] = cash + (btc_holdings * price) # current portfolio value

    df.loc[:start_idx, 'portfolio_value'] = initial_capital

    return {
        'strategy': f'MA Crossover ({short_window}/{long_window})',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
