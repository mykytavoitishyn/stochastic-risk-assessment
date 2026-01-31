import pandas as pd


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI (Relative Strength Index)."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def rsi_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    rsi_period: int = 14,
    oversold_threshold: int = 30,
    overbought_threshold: int = 70,
) -> dict:
    """
    RSI strategy: buy when oversold, sell when overbought.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        initial_capital: Starting capital in USDT
        rsi_period: Period for RSI calculation
        oversold_threshold: Buy when RSI crosses below this
        overbought_threshold: Sell when RSI crosses above this

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    df['rsi'] = calculate_rsi(df['close_price'], period=rsi_period)
    df['prev_rsi'] = df['rsi'].shift(1)
    df['buy_signal'] = (df['prev_rsi'] >= oversold_threshold) & (df['rsi'] < oversold_threshold)
    df['sell_signal'] = (df['prev_rsi'] <= overbought_threshold) & (df['rsi'] > overbought_threshold)

    cash = initial_capital
    btc_holdings = 0.0
    df['portfolio_value'] = 0.0

    start_idx = rsi_period + 1
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

    # Fill initial values
    df.loc[:start_idx, 'portfolio_value'] = initial_capital

    return {
        'strategy': f'RSI ({rsi_period}) [{oversold_threshold}/{overbought_threshold}]',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
