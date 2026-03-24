import pandas as pd

def load_df(
        ticker: str,
        timeframe: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:

    fpath = f"data/org/marketdata/{ticker}_{timeframe}_{start_date}_{end_date}.csv"
    df = pd.read_csv(fpath, index_col=0)

    df["close_time"] = pd.to_datetime(df["close_time"])
    return df