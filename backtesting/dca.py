import pandas as pd


def dca_backtest(
    df: pd.DataFrame,
    investment_amount: float = 100.0,
    frequency: str = 'weekly',
    total_budget: float = None,
) -> dict:
    """
    Dollar Cost Averaging: invest fixed amount at regular intervals.

    Parameters:
        df: DataFrame with 'close_price' and 'open_time' columns
        investment_amount: Amount to invest per period in USDT
        frequency: 'daily', 'weekly', 'biweekly', 'monthly'
        total_budget: Max total to invest (None = unlimited)

    Returns:
        dict with portfolio_values Series and trade info
    """
    df = df.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.sort_values('open_time').reset_index(drop=True)

    freq_map = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'monthly': 30}
    if frequency not in freq_map:
        raise ValueError(f"Frequency must be one of {list(freq_map.keys())}")

    interval_days = freq_map[frequency]

    btc_amount = 0.0
    total_invested = 0.0
    num_purchases = 0
    purchase_history = []

    df['portfolio_value'] = 0.0
    last_purchase_idx = -interval_days

    for idx, row in df.iterrows():
        if idx - last_purchase_idx >= interval_days:
            if total_budget is None or total_invested + investment_amount <= total_budget:
                price = row['close_price']
                btc_purchased = investment_amount / price
                btc_amount += btc_purchased
                total_invested += investment_amount
                num_purchases += 1
                last_purchase_idx = idx

                purchase_history.append({
                    'date': row['open_time'],
                    'price': price,
                    'amount_invested': investment_amount,
                    'btc_purchased': btc_purchased,
                })

        df.at[idx, 'portfolio_value'] = btc_amount * row['close_price']

    avg_purchase_price = total_invested / btc_amount if btc_amount > 0 else 0

    return {
        'strategy': f'DCA ({frequency})',
        'initial_capital': total_invested,
        'total_invested': total_invested,
        'avg_purchase_price': avg_purchase_price,
        'btc_amount': btc_amount,
        'num_purchases': num_purchases,
        'frequency': frequency,
        'investment_per_period': investment_amount,
        'portfolio_values': df['portfolio_value'],
        'prices': df['close_price'],
        'timestamps': df['open_time'],
        'purchase_history': purchase_history,
    }
