#saves merged data to a local parquet file for future use, avoiding the need to pull the entire database every time
import os
from .config import LOCAL_DATA_PATH

def save_local_data(df):
    os.makedirs(os.path.dirname(LOCAL_DATA_PATH), exist_ok=True)
    df.to_parquet(LOCAL_DATA_PATH, index=False)