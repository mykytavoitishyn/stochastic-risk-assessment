import pandas as pd


def buy_and_hold_backtest(df: pd.DataFrame, initial_capital: float = 10000.0) -> dict:
    """
    Buy and hold strategy: buy at first price, hold until end.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        initial_capital: Starting capital in USDT

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()

    entry_price = df['close_price'].iloc[0]
    exit_price = df['close_price'].iloc[-1]
    btc_amount = initial_capital / entry_price

    df['portfolio_value'] = btc_amount * df['close_price']

    return {
        'strategy': 'Buy and Hold',
        'initial_capital': initial_capital,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'btc_amount': btc_amount,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'] if 'open_time' in df.columns else None
    }
