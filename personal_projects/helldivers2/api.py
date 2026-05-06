#below are commands to put in terminal
#cd personal_projects/helldivers2   
#uvicorn api:app --reload 



#[
#   {"timestamp": "2026-05-01 00:00:00", "total_players": 60000},
#   {"timestamp": "2026-05-01 01:00:00", "total_players": 62000},
#   {"timestamp": "2026-05-01 02:00:00", "total_players": 64000},
#   {"timestamp": "2026-05-01 03:00:00", "total_players": 66000},
#   {"timestamp": "2026-05-01 04:00:00", "total_players": 68000},
#   {"timestamp": "2026-05-01 05:00:00", "total_players": 70000},
#   {"timestamp": "2026-05-01 06:00:00", "total_players": 72000},
#   {"timestamp": "2026-05-01 07:00:00", "total_players": 74000},
#   {"timestamp": "2026-05-01 08:00:00", "total_players": 75000},
#   {"timestamp": "2026-05-01 09:00:00", "total_players": 74000},
#   {"timestamp": "2026-05-01 10:00:00", "total_players": 72000},
#   {"timestamp": "2026-05-01 11:00:00", "total_players": 70000},
#   {"timestamp": "2026-05-01 12:00:00", "total_players": 68000},
#   {"timestamp": "2026-05-01 13:00:00", "total_players": 66000},
#   {"timestamp": "2026-05-01 14:00:00", "total_players": 64000},
#   {"timestamp": "2026-05-01 15:00:00", "total_players": 62000},
#   {"timestamp": "2026-05-01 16:00:00", "total_players": 60000},
#   {"timestamp": "2026-05-01 17:00:00", "total_players": 58000},
#   {"timestamp": "2026-05-01 18:00:00", "total_players": 56000},
#   {"timestamp": "2026-05-01 19:00:00", "total_players": 54000},
#   {"timestamp": "2026-05-01 20:00:00", "total_players": 52000},
#   {"timestamp": "2026-05-01 21:00:00", "total_players": 50000},
#   {"timestamp": "2026-05-01 22:00:00", "total_players": 48000},
#   {"timestamp": "2026-05-01 23:00:00", "total_players": 46000},
#   {"timestamp": "2026-05-02 00:00:00", "total_players": 44000}
# ]




from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import List

class DataPoint(BaseModel):
    timestamp: str
    total_players: float
app = FastAPI()

# =========================
# LOAD MODEL
# =========================
model = None

try:
    model = joblib.load("modeling/delta_model.pkl")
except Exception as e:
    print(f"Model failed to load: {e}")
# model = joblib.load("modeling/delta_model.pkl")

# =========================
# HELPER: FEATURE CREATION
# =========================
def create_features(df):
    # assume df is sorted by timestamp

    for lag in [1,2,3,6,12,24]:
        df[f"lag_{lag}"] = df["total_players"].shift(lag)

    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    df["same_hour_yesterday"] = df["lag_24"]

    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    return df


FEATURES = [
    "lag_1","lag_2","lag_3",
    "lag_6","lag_12","lag_24",
    "hour_sin","hour_cos",
    "same_hour_yesterday"
]


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {"message": "Helldivers Player Prediction API is running"}


# # =========================
# # PREDICT ENDPOINT
# # =========================
# @app.post("/predict")
# def predict(data: List[DataPoint]):
#     df = pd.DataFrame([d.dict() for d in data])

#     df = df.sort_values("timestamp")

#     df = create_features(df)
    
#     if df.empty:
#         return {"error": "Not enough data after feature engineering"}
#     latest_row = df.iloc[-1:]

#     X = latest_row[FEATURES]

#     delta_pred = model.predict(X)[0]

#     current_players = latest_row["total_players"].values[0]

#     prediction = current_players + delta_pred
#     status = detect_data_issue(df)
#     # 🔥 SAVE TO DB
#     insert_prediction(current_players, prediction, delta_pred, status)
#     return {
#         "current_players": float(current_players),
#         "predicted_next_hour": float(prediction),
#         "delta": float(delta_pred),
#         "data_status": status,
#         "source": "postgres"
#     }


import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # return psycopg2.connect(
    #     host=os.getenv("PGHOST"),
    #     port=os.getenv("PGPORT"),
    #     database=os.getenv("PGDATABASE"),
    #     user=os.getenv("PGUSER"),
    #     password=os.getenv("PGPASSWORD"),
    #     sslmode="require"
    # )
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# 🔥 ADD IT RIGHT HERE
def insert_prediction(current_players, predicted, delta, status):
    query = """
        INSERT INTO player_predictions (
            prediction_time,
            current_players,
            predicted_next_hour,
            delta,
            data_status
        )
        VALUES (NOW(), %s, %s, %s, %s)
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, (current_players, predicted, delta, status))

    conn.commit()
    cur.close()
    conn.close()


from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


def fetch_recent_data(limit=500):
    query = f"""
        SELECT 
            timestamp,
            SUM(player_on_planet) AS total_players
        FROM planet_history
        GROUP BY timestamp
        ORDER BY timestamp DESC
        LIMIT {limit}
    """

    df = pd.read_sql(query, engine)

    # chronological order
    df = df.sort_values("timestamp")

    return df

@app.get("/health")
def health():

    # -------------------------
    # MODEL STATUS
    # -------------------------
    model_loaded = model is not None

    # -------------------------
    # DATABASE STATUS
    # -------------------------
    db_status = "offline"
    latest_timestamp = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT MAX(timestamp)
            FROM planet_history
        """)

        latest_timestamp = cur.fetchone()[0]

        cur.close()
        conn.close()

        db_status = "connected"

    except Exception as e:
        print("HEALTH DB ERROR:", e)

    # -------------------------
    # API RESPONSE
    # -------------------------
    return {
        "api": "online",
        "database": db_status,
        "model_loaded": model_loaded,
        "latest_data_timestamp": latest_timestamp
    }


@app.get("/predict-live")
def predict_live():

    df = fetch_recent_data(limit=600)

    df = create_features(df)
    
    if df.empty:
        return {"error": "Not enough data after feature engineering"}
    latest_row = df.iloc[-1:]

    current_players = latest_row["total_players"].values[0]

    # -------------------------
    # DATA QUALITY CHECK
    # -------------------------
    status = detect_data_issue(df)

    if status == "likely_missing_planets":
        insert_prediction(current_players, None, None, status)

        return {
            "current_players": float(current_players),
            "predicted_next_hour": None,
            "delta": None,
            "data_status": status,
            "source": "postgres"
        }

    # -------------------------
    # MODEL PREDICTION
    # -------------------------
    X = latest_row[FEATURES]
    #make sure the model is loaded before trying to predict
    if model is None:
        return {
            "error": "Model not loaded"
        }
    delta_pred = model.predict(X)[0]

    prediction = current_players + delta_pred
    status = detect_data_issue(df)
    # 🔥 ADD THIS LINE (you forgot it)
    insert_prediction(current_players, prediction, delta_pred, status)

    return {
        "current_players": float(current_players),
        "predicted_next_hour": float(prediction),
        "delta": float(delta_pred),
        "data_status": status,
        "source": "postgres"
    }
    
#major order stats
# @app.get("/major-order-status")
# def major_order_status():

#     query = """
#         SELECT
#             timestamp,
#             major_order_id,
#             major_order_dispatch,

#             SUM(
#                 CASE
#                     WHEN in_major_order = 'T'
#                     THEN player_on_planet
#                     ELSE 0
#                 END
#             ) AS players_in_major_order,

#             SUM(
#                 CASE
#                     WHEN in_major_order != 'T'
#                     THEN player_on_planet
#                     ELSE 0
#                 END
#             ) AS players_outside_major_order,

#             SUM(player_on_planet) AS total_players

#         FROM planet_history

#         WHERE timestamp = (
#             SELECT MAX(timestamp)
#             FROM planet_history
#         )

#         GROUP BY
#             timestamp,
#             major_order_id,
#             major_order_dispatch
#     """

#     df = pd.read_sql(query, engine)

#     if df.empty:
#         return {"error": "No major order data found"}

#     row = df.iloc[0]

#     players_in = float(row["players_in_major_order"])
#     players_out = float(row["players_outside_major_order"])
#     total_players = float(row["total_players"])

#     mo_ratio = (
#         players_in / total_players
#         if total_players > 0
#         else 0
#     )

#     return {
#         "timestamp": str(row["timestamp"]),
#         "major_order_id": int(row["major_order_id"]) if pd.notna(row["major_order_id"]) else None,
#         "major_order_dispatch": row["major_order_dispatch"],

#         "players_in_major_order": players_in,
#         "players_outside_major_order": players_out,
#         "total_players": total_players,

#         "major_order_ratio": round(mo_ratio, 3)
#     }

@app.get("/major-order-status")
def major_order_status():

    # -------------------------
    # FETCH CURRENT SNAPSHOT
    # -------------------------
    query = """
        SELECT
            timestamp,
            major_order_id,
            major_order_dispatch,
            in_major_order,
            player_on_planet

        FROM planet_history

        WHERE timestamp = (
            SELECT MAX(timestamp)
            FROM planet_history
        )
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {"error": "No major order data found"}

    # -------------------------
    # DATA QUALITY STATUS
    # -------------------------
    total_players = df["player_on_planet"].sum()

    historical_query = """
        SELECT
            timestamp,
            SUM(player_on_planet) AS total_players
        FROM planet_history
        GROUP BY timestamp
        ORDER BY timestamp
        LIMIT 1000
    """

    hist_df = pd.read_sql(historical_query, engine)

    status = detect_data_issue(hist_df)

    # -------------------------
    # MAJOR ORDER METRICS
    # -------------------------
    players_in = df.loc[
        df["in_major_order"] == "T",
        "player_on_planet"
    ].sum()

    players_out = df.loc[
        df["in_major_order"] != "T",
        "player_on_planet"
    ].sum()

    mo_ratio = (
        players_in / total_players
        if total_players > 0
        else 0
    )

    latest = df.iloc[0]

    # -------------------------
    # RESPONSE
    # -------------------------
    return {
    "server_health": {
        "status": status,
        "warning": (
            "Current data likely incomplete due to missing planets/API issues"
            if status == "likely_missing_planets"
            else None
        )
    },

    "major_order_data": {
        "timestamp": str(latest["timestamp"]),

        "major_order_id": (
            int(latest["major_order_id"])
            if pd.notna(latest["major_order_id"])
            else None
        ),

        "major_order_dispatch": latest["major_order_dispatch"],

        "players_in_major_order": int(players_in),
        "players_outside_major_order": int(players_out),
        "total_players": int(total_players),

        "major_order_ratio": round(float(mo_ratio), 3)
    }
}
    
@app.get("/major-order-history-by-day")
def major_order_history_by_day(days_ago: int = 5):

    # -------------------------
    # FIND TARGET MAJOR ORDER
    # -------------------------
    major_order_query = f"""
        SELECT
            major_order_id,
            major_order_dispatch,
            timestamp

        FROM planet_history

        WHERE timestamp <= NOW() - INTERVAL '{days_ago} days'
            AND major_order_id IS NOT NULL

        ORDER BY timestamp DESC

        LIMIT 1
    """

    mo_df = pd.read_sql(major_order_query, engine)

    if mo_df.empty:
        return {"error": "No major order found for requested date"}

    target_major_order_id = mo_df.iloc[0]["major_order_id"]
    dispatch = mo_df.iloc[0]["major_order_dispatch"]

    # -------------------------
    # GET HISTORY FOR ONLY THAT MO
    # -------------------------
    history_query = f"""
        SELECT
            timestamp,

            SUM(
                CASE
                    WHEN in_major_order = 'T'
                    THEN player_on_planet
                    ELSE 0
                END
            ) AS players_in_major_order,

            SUM(
                CASE
                    WHEN in_major_order != 'T'
                    THEN player_on_planet
                    ELSE 0
                END
            ) AS players_outside_major_order,

            SUM(player_on_planet) AS total_players

        FROM planet_history

        WHERE major_order_id = {int(target_major_order_id)}

        GROUP BY timestamp

        ORDER BY timestamp
    """

    df = pd.read_sql(history_query, engine)

    if df.empty:
        return {"error": "No history found for this major order"}

    # -------------------------
    # MAJOR ORDER RATIO
    # -------------------------
    df["major_order_ratio"] = (
        df["players_in_major_order"] /
        df["total_players"]
    ).fillna(0)

    # -------------------------
    # BUILD RESPONSE
    # -------------------------
    history = []

    for _, row in df.iterrows():

        history.append({
            "timestamp": str(row["timestamp"]),
            "players_in_major_order": int(row["players_in_major_order"]),
            "players_outside_major_order": int(row["players_outside_major_order"]),
            "total_players": int(row["total_players"]),
            "major_order_ratio": round(float(row["major_order_ratio"]), 3)
        })

    return {
        "query_days_ago": days_ago,

        "major_order_id": int(target_major_order_id),

        "major_order_dispatch": dispatch,

        "history": history
    }
    
    
@app.get("/forecast-24h")
def forecast_24h():

    if model is None:
        return {"error": "Model not loaded"}

    # -------------------------
    # FETCH RECENT DATA
    # -------------------------
    df = fetch_recent_data(limit=600)

    df = create_features(df)

    if df.empty:
        return {"error": "Not enough historical data"}

    # -------------------------
    # DATA HEALTH CHECK
    # -------------------------
    status = detect_data_issue(df)

    if status != "ok":
        return {
            "server_health": {
                "status": status,
                "warning": "Forecast disabled due to unreliable live data"
            }
        }

    # -------------------------
    # START RECURSIVE FORECAST
    # -------------------------
    working_df = df.copy()

    forecasts = []

    for step in range(1, 25):

        latest_row = working_df.iloc[-1:]

        X = latest_row[FEATURES]

        delta_pred = model.predict(X)[0]

        current_players = latest_row["total_players"].values[0]

        next_players = current_players + delta_pred

        next_timestamp = (
            pd.to_datetime(latest_row["timestamp"].values[0])
            + pd.Timedelta(hours=1)
        )

        forecasts.append({
            "hour_ahead": step,
            "timestamp": str(next_timestamp),
            "predicted_players": int(next_players)
        })

        # -------------------------
        # APPEND PREDICTED ROW
        # -------------------------
        new_row = pd.DataFrame([{
            "timestamp": next_timestamp,
            "total_players": next_players
        }])

        working_df = pd.concat(
            [working_df[["timestamp", "total_players"]], new_row],
            ignore_index=True
        )

        working_df = create_features(working_df)

    return {
        "server_health": {
            "status": status
        },

        "forecast_horizon_hours": 24,

        "forecast": forecasts
    }
    
@app.get("/top-planets")
def top_planets(limit: int = 10):

    query = f"""
        SELECT
            name,
            player_on_planet,
            "currentOwner",
            in_major_order,
            strategic_opportunity,
            possible_paths_to_major_order,
            sector,
            timestamp
        FROM planet_history
        WHERE timestamp = (
            SELECT MAX(timestamp)
            FROM planet_history
        )
        ORDER BY player_on_planet DESC
        LIMIT {limit}
    """

    df = pd.read_sql(query, engine)

    status = detect_data_issue(df.rename(columns={
        "player_on_planet": "total_players"
    }))

    planets = []

    for _, row in df.iterrows():

        planets.append({
            "planet": row["name"],
            "players": int(row["player_on_planet"]),
            "owner": row["currentOwner"],
            "in_major_order": row["in_major_order"],
            "sector": row["sector"],
            "strategic_opportunity": "Strategic Opportunity",
            "possible_paths_to_major_order": "Possible Paths To MO",
        })

    return {
        "server_health": {
            "status": status
        },

        "top_planets": planets
    }

@app.get("/faction-summary")
def faction_summary():

    query = """
        SELECT
            "currentOwner",
            SUM(player_on_planet) as total_players
        FROM planet_history
        WHERE timestamp = (
            SELECT MAX(timestamp)
            FROM planet_history
        )
        GROUP BY "currentOwner"
        ORDER BY total_players DESC
    """

    df = pd.read_sql(query, engine)

    status = detect_data_issue(
        df.rename(columns={
            "total_players": "total_players"
        })
    )

    factions = []

    for _, row in df.iterrows():

        factions.append({
            "faction": row["currentOwner"],
            "players": int(row["total_players"])
        })

    return {
        "server_health": {
            "status": status
        },

        "factions": factions
    }
    
    
@app.get("/forecast-vs-actual")
def forecast_vs_actual(history_hours: int = 24):

    if model is None:
        return {"error": "Model not loaded"}

    # -------------------------
    # FETCH HISTORICAL DATA
    # -------------------------
    historical_df = fetch_recent_data(limit=600)

    historical_df = historical_df.sort_values("timestamp")

    actual_df = historical_df.tail(history_hours).copy()

    # -------------------------
    # FEATURE ENGINEERING
    # -------------------------
    working_df = create_features(historical_df.copy())

    if working_df.empty:
        return {"error": "Not enough historical data"}

    status = detect_data_issue(working_df)

    if status != "ok":
        return {
            "server_health": {
                "status": status
            }
        }

    # -------------------------
    # FORECAST
    # -------------------------
    forecasts = []

    for step in range(1, 25):

        latest_row = working_df.iloc[-1:]

        X = latest_row[FEATURES]

        delta_pred = model.predict(X)[0]

        current_players = latest_row["total_players"].values[0]

        next_players = current_players + delta_pred

        next_timestamp = (
            pd.to_datetime(latest_row["timestamp"].values[0])
            + pd.Timedelta(hours=1)
        )

        forecasts.append({
            "timestamp": str(next_timestamp),
            "players": float(next_players),
            "type": "Forecast"
        })

        # append recursive prediction
        new_row = pd.DataFrame([{
            "timestamp": next_timestamp,
            "total_players": next_players
        }])

        temp_df = pd.concat(
            [
                working_df[["timestamp", "total_players"]],
                new_row
            ],
            ignore_index=True
        )

        working_df = create_features(temp_df)

    # -------------------------
    # ACTUAL DATA
    # -------------------------
    actuals = []

    for _, row in actual_df.iterrows():

        actuals.append({
            "timestamp": str(row["timestamp"]),
            "players": float(row["total_players"]),
            "type": "Actual"
        })

    # -------------------------
    # RETURN COMBINED
    # -------------------------
    return {
        "server_health": {
            "status": status
        },

        "data": actuals + forecasts
    }

def detect_data_issue(df):
    current = df["total_players"].iloc[-1]

    # older stable history, not the most recent broken data
    #historical = df["total_players"].iloc[-500:-48]
    historical = df["total_players"].iloc[-500:-48]

    if len(historical) < 50:
        return "insufficient_history"
    baseline = historical.median()

    # tune this number
    lower_bound = baseline * 0.70
    high_event_bound = baseline * 2.5

    print(
        f"CURRENT: {current} | "
        f"BASELINE_MEDIAN: {baseline} | "
        f"LOWER_BOUND: {lower_bound} | "
        f"HIGH_EVENT_BOUND: {high_event_bound}"
    )

    if current < lower_bound:
        return "likely_missing_planets"

    if current > high_event_bound:
        return "high_activity_event"

    return "ok"

def insert_prediction(current_players, predicted, delta, status):
    try:
        # FORCE clean types
        current_players = float(current_players) if current_players is not None else None
        predicted = float(predicted) if predicted is not None else None
        delta = float(delta) if delta is not None else None

        query = """
            INSERT INTO player_predictions (
                prediction_time,
                current_players,
                predicted_next_hour,
                delta,
                data_status
            )
            VALUES (NOW(), %s, %s, %s, %s)
        """

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(query, (current_players, predicted, delta, status))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("🔥 INSERT ERROR:", e)
        raise
    
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)