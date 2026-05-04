#loads local data from a parquet file
import pandas as pd
import os
from .config import LOCAL_DATA_PATH

def load_local_data():
    if os.path.exists(LOCAL_DATA_PATH):
        df = pd.read_parquet(LOCAL_DATA_PATH)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    return pd.DataFrame()