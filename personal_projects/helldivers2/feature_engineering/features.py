import pandas as pd
import numpy as np

# =========================================
# LAG FEATURES
# =========================================

def add_lag_features(df):

    #df = df.copy()

    lags = [1,2, 3, 4, 6, 12, 23, 24, 25, 48, 72, 168]

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

    #df = df.copy()

    windows = [3, 6, 24]

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

    # =====================================
    # VOLATILITY RATIOS
    # =====================================

    df["volatility_ratio_6"] = (
        df["rolling_std_6"]
        / df["rolling_mean_6"]
    )

    df["volatility_ratio_24"] = (
        df["rolling_std_24"]
        / df["rolling_mean_24"]
    )

    return df


# =========================================
# EMA FEATURES
# =========================================

def add_ema_features(df):

    #df = df.copy()

    df["ema_3"] = (
        df["total_players"]
        .shift(1)
        .ewm(span=3)
        .mean()
    )

    df["ema_6"] = (
        df["total_players"]
        .shift(1)
        .ewm(span=6)
        .mean()
    )

    df["ema_12"] = (
        df["total_players"]
        .shift(1)
        .ewm(span=12)
        .mean()
    )

    # =====================================
    # EMA MOMENTUM
    # =====================================

    df["ema_diff_3_12"] = (
        df["ema_3"]
        - df["ema_12"]
    )

    df["ema_ratio_3_12"] = (
        df["ema_3"]
        / df["ema_12"]
    )

    df["ratio_to_ema_6"] = (
        df["total_players"]
        / df["ema_6"]
    )

    return df


# =========================================
# TIME FEATURES
# =========================================

def add_time_features(df):

    #df = df.copy()

    df["hour"] = (
        df["timestamp"]
        .dt.hour
    )

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

    df["dayofweek_sin"] = np.sin(
        2 * np.pi * df["dayofweek"] / 7
    )

    df["dayofweek_cos"] = np.cos(
        2 * np.pi * df["dayofweek"] / 7
    )

    df["is_weekend"] = (
        df["dayofweek"] >= 5
    ).astype(int)

    return df


# =========================================
# MOMENTUM FEATURES
# =========================================

def add_momentum_features(df):

    #df = df.copy()

    # =====================================
    # BASIC DELTAS
    # =====================================

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
    
    df["delta_168"] = (
        df["total_players"]
        - df["lag_168"]
    )

    # =====================================
    # ACCELERATION
    # =====================================

    df["delta_1_change"] = (
        df["delta_1"]
        - df["delta_1"].shift(1)
    )

    # =====================================
    # TREND FEATURES
    # =====================================

    df["rolling_trend_6"] = (
        df["total_players"]
        .diff()
        .rolling(6)
        .mean()
    )

    df["rolling_trend_24"] = (
        df["total_players"]
        .diff()
        .rolling(24)
        .mean()
    )

    # =====================================
    # LAG COMPARISONS
    # =====================================

    df["lag1_vs_24"] = (
        df["lag_1"]
        - df["lag_24"]
    )

    df["lag1_vs_168"] = (
        df["lag_1"]
        - df["lag_168"]
    )
    
    # =====================================
    # WEEK OVER WEEK CHANGE
    # =====================================

    df["delta_vs_168"] = (
        df["total_players"]
        - df["lag_168"]
    )

    # =====================================
    # WEEK OVER WEEK RATIO
    # =====================================

    df["ratio_vs_168"] = (
        df["total_players"]
        / (df["lag_168"] + 1)
    )
    
    # =====================================
    # TREND ACCELERATION
    # =====================================

    df["rolling_trend_change_6"] = (
        df["rolling_trend_6"]
        - df["rolling_trend_6"].shift(1)
    )
    
    # =====================================
    # MAJOR ORDER ENGAGEMENT FEATURES
    # =====================================

    df["mo_ratio_change_3"] = (
        df["mo_ratio"]
        - df["mo_ratio"].shift(3)
    )

    df["frontline_ratio_change_3"] = (
        df["frontline_ratio"]
        - df["frontline_ratio"].shift(3)
    )

    df["strategic_ratio_change_3"] = (
        df["strategic_ratio"]
        - df["strategic_ratio"].shift(3)
    )
    
    

    return df





# =========================================
# EXTREME / SPIKE FEATURES
# =========================================

def add_extreme_features(df):

    #df = df.copy()

    df["rolling_max_6"] = (
        df["total_players"]
        .shift(1)
        .rolling(6)
        .max()
    )

    df["rolling_min_6"] = (
        df["total_players"]
        .shift(1)
        .rolling(6)
        .min()
    )

    df["distance_from_recent_peak"] = (
        df["rolling_max_6"]
        - df["total_players"]
    )

    df["distance_from_recent_bottom"] = (
        df["total_players"]
        - df["rolling_min_6"]
    )

    # =====================================
    # SPIKE FLAGS
    # =====================================

    df["sudden_spike"] = (
        df["delta_1"] > 5000
    ).astype(int)

    df["sudden_drop"] = (
        df["delta_1"] < -5000
    ).astype(int)

    return df


# =========================================
# INTERACTION FEATURES
# =========================================

def add_interaction_features(df):

    #df = df.copy()

    df["delta_x_hour"] = (
        df["delta_1"]
        * df["hour"]
    )

    df["ema_diff_x_weekend"] = (
        df["ema_diff_3_12"]
        * df["is_weekend"]
    )

    return df



def add_warbond_features(df):
    

    # =====================================
    # COPY
    # =====================================

    #df = df.copy()

    # =====================================
    # WARBOND DEFINITIONS
    # =====================================

    WARBONDS = [

        {
            #"warbond_id": 1,

            "title": "EXO EXPERTS",

            "announcement_date": "2026-04-21",

            "release_date": "2026-04-28"
        },

        # add more warbonds here, rest will take care of the logic
    ]

    # =====================================
    # INITIALIZE COLUMNS
    # =====================================

    df["warbond_id"] = 0

    df["warbond_active"] = 0

    df["warbond_announcement_active"] = 0

    df["hours_until_warbond"] = -999.0

    df["hours_since_warbond"] = -999.0
    #the below column will help show player increase due to warbond with an exponential curve applied later
    df["warbond_uplift"] = 1.0
    


    # =====================================
    # FEATURE CREATION
    # =====================================

    #for wb in WARBONDS:
    # for i, wb in enumerate(WARBONDS):

    #     warbond_id = i + 1
    
    for i, wb in enumerate(WARBONDS):

        warbond_id = i + 1

        announcement_date = pd.to_datetime(
            wb["announcement_date"]
        )

        release_date = pd.to_datetime(
            wb["release_date"]
        )

        # ==============================
        # WARBOND ID
        # ==============================

        post_release_mask = (

            (df["timestamp"] >= release_date)

            &

        (
            df["timestamp"]
            <
            release_date
            + pd.Timedelta(days=30)
        )
        )
        # post_release_mask = (
        #     df["timestamp"] >= release_date
        # )

        df.loc[
            post_release_mask,
            "warbond_id"
        ] = warbond_id
    

        # announcement_date = pd.to_datetime(
        #     wb["announcement_date"]
        # )

        # release_date = pd.to_datetime(
        #     wb["release_date"]
        # )

        # # ==============================
        # # WARBOND ID
        # # ==============================

        # post_release_mask = (
        #     df["timestamp"] >= release_date
        # )

        # df.loc[
        #     post_release_mask,
        #     "warbond_id"
        # ] = wb["warbond_id"]

        # ==============================
        # ANNOUNCEMENT ACTIVE
        # ==============================

        announcement_mask = (

            (df["timestamp"] >= announcement_date)

            &

            (df["timestamp"] < release_date)
        )

        df.loc[
            announcement_mask,
            "warbond_announcement_active"
        ] = 1

        # ==============================
        # RELEASE ACTIVE
        # ==============================

        release_window_mask = (

            (df["timestamp"] >= release_date)

            &

            (
                df["timestamp"]
                <
                release_date
                + pd.Timedelta(days=7)
            )
        )

        df.loc[
            release_window_mask,
            "warbond_active"
        ] = 1

        # ==============================
        # HOURS UNTIL
        # ==============================

        # pre_release_mask = (
        #     df["timestamp"] < release_date
        # )
        
        pre_release_mask = (

        (df["timestamp"] >= announcement_date)

        &

        (df["timestamp"] < release_date)
        )

        hours_until = (

            release_date
            -
            df.loc[
                pre_release_mask,
                "timestamp"
            ]

        ).dt.total_seconds() / 3600

        df.loc[
            pre_release_mask,
            "hours_until_warbond"
        ] = hours_until

        # ==============================
        # HOURS SINCE
        # ==============================

        hours_since = (

            df.loc[
                post_release_mask,
                "timestamp"
            ]
            -
            release_date

        ).dt.total_seconds() / 3600

        df.loc[
            post_release_mask,
            "hours_since_warbond"
        ] = hours_since
        #below is for warbond uplift feature
        uplift = np.exp(

            -hours_since / 72
        )
        #scale it
        uplift = 1 + (uplift * 0.5)
        df.loc[
            post_release_mask,
            "warbond_uplift"
        ] = uplift
    return df


def create_fourier_features(
    df,
    daily_order=5,
    weekly_order=3
):

    t = np.arange(len(df))

    # =====================================
    # DAILY FOURIER FEATURES
    # =====================================

    for k in range(1, daily_order + 1):

        df[f"daily_sin_{k}"] = np.sin(
            2 * np.pi * k * t / 24
        )

        df[f"daily_cos_{k}"] = np.cos(
            2 * np.pi * k * t / 24
        )

    # =====================================
    # WEEKLY FOURIER FEATURES
    # =====================================

    for k in range(1, weekly_order + 1):

        df[f"weekly_sin_{k}"] = np.sin(
            2 * np.pi * k * t / 168
        )

        df[f"weekly_cos_{k}"] = np.cos(
            2 * np.pi * k * t / 168
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

    # =====================================
    # SORT
    # =====================================

    df = (
        df
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    # =====================================
    # FEATURE GROUPS
    # =====================================

    if feature_groups.get("lags", False):

        df = add_lag_features(df)

    if feature_groups.get("rolling", False):

        df = add_rolling_features(df)

    if feature_groups.get("ema", False):

        df = add_ema_features(df)

    if feature_groups.get("time", False):

        df = add_time_features(df)

    if feature_groups.get("momentum", False):

        df = add_momentum_features(df)

    if feature_groups.get("extremes", False):

        df = add_extreme_features(df)

    if feature_groups.get("interactions", False):

        df = add_interaction_features(df)
    
    if feature_groups.get("warbonds", False):
        df = add_warbond_features(df)
    if feature_groups.get("fourier", False):
        df = create_fourier_features(df)

    return df