#steps to take for incremental data pipeline, this avoids unnecessary data pulls and processing by only fetching 
# new records from the database and merging them with local data

from .load_local import load_local_data
from .fetch_db import fetch_new_data
from .merge import merge_data
from .save import save_local_data

def get_latest_timestamp(df):
    if df.empty:
        return None
    return df["timestamp"].max()

def run_incremental_pipeline():
    print("Loading local data...")
    local_df = load_local_data()

    latest_ts = get_latest_timestamp(local_df)
    print("Latest timestamp:", latest_ts)

    print("Fetching new data...")
    new_df = fetch_new_data(latest_ts)
    print(f"Fetched {len(new_df)} rows")

    if new_df.empty:
        print("No new data.")
        return local_df

    updated_df = merge_data(local_df, new_df)

    print("Saving data...")
    save_local_data(updated_df)

    return updated_df