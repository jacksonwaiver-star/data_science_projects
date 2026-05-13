import pandas as pd


def aggregate_total_players(df):

    df = df.copy()

    # ensure datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    ts_players = (

        df.groupby("timestamp")[
            "player_on_planet"
        ]
        .sum()
        .reset_index()
    )

    ts_players = ts_players.rename(
        columns={
            "player_on_planet":
            "total_players"
        }
    )

    ts_players = ts_players.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return ts_players