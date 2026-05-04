#merges new data from db pull with local data
import pandas as pd

def merge_data(local_df, new_df):
    if local_df.empty:
        return new_df

    combined = pd.concat([local_df, new_df], ignore_index=True)

    combined = combined.drop_duplicates(
        subset=["planet_index", "timestamp"]
    )

    return combined