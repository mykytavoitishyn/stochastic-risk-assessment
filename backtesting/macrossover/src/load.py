import pandas as pd

def load_df(datapath: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = pd.read_csv(datapath, index_col=0)
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df[(df["open_time"] >= start_date) & (df["open_time"] <= end_date)]
    return df