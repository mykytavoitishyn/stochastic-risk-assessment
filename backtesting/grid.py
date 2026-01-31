import pandas as pd


def grid_trading_backtest(
    df: pd.DataFrame,
    initial_capital: float = 10000.0,
    grid_spacing_pct: float = 0.05,
    num_grids: int = 10,
    investment_per_grid: float = 1000.0,
) -> dict:
    """
    Grid Trading strategy: buy at intervals below price, sell at intervals above.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        initial_capital: Starting capital in USDT
        grid_spacing_pct: Percentage spacing between grid levels
        num_grids: Number of grid levels above and below starting price
        investment_per_grid: Amount to invest at each grid level

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    start_price = df['close_price'].iloc[0]

    # Create grid levels
    grid_levels = []
    for i in range(-num_grids, num_grids + 1):
        if i == 0:
            continue
        grid_levels.append({
            'level': i,
            'price': start_price * (1 + (i * grid_spacing_pct)),
            'type': 'buy' if i < 0 else 'sell',
            'triggered': False,
            'btc_amount': 0.0
        })
    grid_levels = sorted(grid_levels, key=lambda x: x['price'])

    cash = initial_capital
    total_btc = 0.0
    df['portfolio_value'] = 0.0

    for idx in range(len(df)):
        price = df.iloc[idx]['close_price']

        for grid in grid_levels:
            if grid['type'] == 'buy' and price <= grid['price'] and not grid['triggered']:
                if cash >= investment_per_grid:
                    btc_purchased = investment_per_grid / price
                    total_btc += btc_purchased
                    cash -= investment_per_grid
                    grid['triggered'] = True
                    grid['btc_amount'] = btc_purchased

            elif grid['type'] == 'sell' and price >= grid['price'] and not grid['triggered']:
                triggered_buys = [g for g in grid_levels if g['type'] == 'buy' and g['triggered'] and g['btc_amount'] > 0]
                if triggered_buys:
                    buy_grid = triggered_buys[0]
                    btc_to_sell = buy_grid['btc_amount']
                    cash += btc_to_sell * price
                    total_btc -= btc_to_sell
                    grid['triggered'] = True
                    buy_grid['triggered'] = False
                    buy_grid['btc_amount'] = 0.0

        df.at[idx, 'portfolio_value'] = cash + (total_btc * price)

    return {
        'strategy': f'Grid Trading ({grid_spacing_pct*100:.0f}%, {num_grids*2} levels)',
        'initial_capital': initial_capital,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
    }
