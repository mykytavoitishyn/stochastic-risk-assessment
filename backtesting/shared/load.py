import pandas as pd

def load_df(
        ticker: str,
        timeframe: str,
        asset_type: str,
    ) -> pd.DataFrame:

    fpath = f"data/org/{asset_type}/{ticker}/{timeframe}.csv"
    df = pd.read_csv(fpath, index_col=0)

    df["close_time"] = pd.to_datetime(df["close_time"])
    return df
