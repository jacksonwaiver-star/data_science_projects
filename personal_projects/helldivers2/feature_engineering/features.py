import pandas as pd
import numpy as np


# =========================================
# LAG FEATURES
# =========================================

def add_lag_features(df):

    df = df.copy()

    lags = [1, 3, 6, 12, 24, 168]

    for lag in lags:

        df[f"lag_{lag}"] = (
            df["total_players"]
            .shift(lag)
        )

    return df


# =========================================
# ROLLING FEATURES
# =========================================

def add_rolling_features(df):

    df = df.copy()

    windows = [6, 24]

    for window in windows:

        df[f"rolling_mean_{window}"] = (
            df["total_players"]
            .shift(1)
            .rolling(window)
            .mean()
        )

        df[f"rolling_std_{window}"] = (
            df["total_players"]
            .shift(1)
            .rolling(window)
            .std()
        )

    return df


# =========================================
# TIME FEATURES
# =========================================

def add_time_features(df):

    df = df.copy()

    df["hour"] = df["timestamp"].dt.hour

    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )

    df["dayofweek"] = (
        df["timestamp"]
        .dt.dayofweek
    )

    df["is_weekend"] = (
        df["dayofweek"] >= 5
    ).astype(int)

    return df


# =========================================
# MOMENTUM FEATURES
# =========================================

def add_momentum_features(df):

    df = df.copy()

    df["delta_1"] = (
        df["total_players"]
        - df["lag_1"]
    )

    df["delta_3"] = (
        df["total_players"]
        - df["lag_3"]
    )

    df["delta_24"] = (
        df["total_players"]
        - df["lag_24"]
    )

    return df


# =========================================
# MAIN FEATURE PIPELINE
# =========================================

def create_features(
    df,
    feature_groups
):

    df = df.copy()

    # Ensure sorted
    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    if feature_groups.get("lags", False):

        df = add_lag_features(df)

    if feature_groups.get("rolling", False):

        df = add_rolling_features(df)

    if feature_groups.get("time", False):

        df = add_time_features(df)

    if feature_groups.get("momentum", False):

        df = add_momentum_features(df)

    return df