import pandas as pd


def mean_reversion_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    ma_period: int = 20,
    buy_threshold: float = 0.05,
    sell_threshold: float = 0.05,
) -> dict:
    """
    Mean Reversion strategy: buy below MA, sell above MA.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        initial_capital: Starting capital in USDT
        ma_period: Period for moving average
        buy_threshold: Buy when price is this % below MA
        sell_threshold: Sell when price is this % above MA

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    df['ma'] = df['close_price'].rolling(window=ma_period).mean()
    df['buy_level'] = df['ma'] * (1 - buy_threshold)
    df['sell_level'] = df['ma'] * (1 + sell_threshold)

    df['buy_signal'] = df['close_price'] < df['buy_level']
    df['sell_signal'] = df['close_price'] > df['sell_level']

    cash = initial_capital
    btc_holdings = 0.0
    df['portfolio_value'] = 0.0

    start_idx = ma_period
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
        'strategy': f'Mean Reversion (MA{ma_period}, ±{buy_threshold*100:.0f}%)',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
