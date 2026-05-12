#below are commands to put in terminal
#cd personal_projects/helldivers2   
#uvicorn api:app --reload 
#https://datascienceprojects-production.up.railway.app/docs#/


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




from sys import path

from urllib import request, response

from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import List
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from cachetools import TTLCache
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import os
from collections import defaultdict
import time



class DataPoint(BaseModel):
    timestamp: str
    total_players: float
#app = FastAPI()



tags_metadata = [

    {
        "name": "System",
        "description": (
            "Health monitoring, deployment status, "
            "database connectivity, and API diagnostics."
        )
    },

    {
        "name": "Forecasting",
        "description": (
            "Machine learning forecasting endpoints using "
            "time-series feature engineering and XGBoost models."
        )
    },

    {
        "name": "Major Orders",
        "description": (
            "Endpoints related to Major Order participation, "
            "historical analytics, and engagement metrics."
        )
    },

    {
        "name": "Planets",
        "description": (
            "Planet-level analytics including active player counts, "
            "ownership, and strategic indicators."
        )
    },

    {
        "name": "Factions",
        "description": (
            "Faction engagement summaries and player distribution "
            "across enemy types."
        )
    },

    {
        "name": "Analytics",
        "description": (
            "General analytics, comparisons, tracking, and "
            "dashboard-related metrics."
        )
    }
]


















app = FastAPI(
    title="Helldivers 2 Analytics API",

    description="""
## Recruiter Demo Access

If you are a recruiter or reviewer:

1. Open the **Authorize** button in the top right.
2. Paste the demo API key provided in my resume.
3. You can then test protected endpoints directly in Swagger UI.

### What This API Includes
- Real-time Helldivers 2 analytics
- Major Order tracking
- Player forecasting
- Faction engagement metrics
- Historical analytics
- Rate limiting + API key security
- Railway deployment + PostgreSQL backend

### Example Endpoints
- `/health`
- `/major-order-status`
- `/forecast-24h`
- `/top-planets`

Built with:
- FastAPI
- PostgreSQL
- XGBoost
- Railway
""",
    openapi_tags=tags_metadata
)



class UserEvent(BaseModel):
    session_id: str
    event_type: str
    element: str
    
    

#add API keys for expensive endpoints and to prevent abuse
API_KEY = os.getenv("API_KEY")
DEMO_API_KEY = os.getenv("DEMO_API_KEY")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)

def verify_api_key(api_key: str = Security(api_key_header)):

    key_map = {
        API_KEY: "owner",
        DEMO_API_KEY: "recruiter"
    }

    if api_key not in key_map:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )

    return key_map[api_key]


@app.post(
    "/track-event",
    include_in_schema=False
)
def track_event(
    event: UserEvent,
    user_type: str = Security(verify_api_key)
):
    # status_code = response.status_code

    # if status_code == 403:
    #     event_type = "unauthorized"

    # elif status_code == 429:
    #     event_type = "rate_limited"

    # else:
    #     event_type = "api_call"
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO user_events (
                session_id,
                event_type,
                element
            )
            VALUES (
                :session_id,
                :event_type,
                :element
            )
        """), {
            "session_id": event.session_id,
            "event_type": event.event_type,
            "element": event.element
        })

    return {"status": "success"}

summary_cache = TTLCache(maxsize=100, ttl=300)

forecast_cache = TTLCache(maxsize=20, ttl=300)

forecast_vs_actual_cache = TTLCache(maxsize=20, ttl=300)

top_planets_cache = TTLCache(maxsize=50, ttl=120)

major_order_cache = TTLCache(maxsize=20, ttl=300)

total_players_cache = TTLCache(maxsize=20, ttl=60)

major_order_history_cache = TTLCache(maxsize=50, ttl=300)

FAILED_ATTEMPTS = defaultdict(int)

BLOCKED_IPS = {}

MAX_FAILED_ATTEMPTS = 5

BLOCK_DURATION_SECONDS = 60 * 30

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"}
    )

#add API keys for expensive endpoints and to prevent abuse
# API_KEY = os.getenv("API_KEY")
# DEMO_API_KEY = os.getenv("DEMO_API_KEY")

# api_key_header = APIKeyHeader(
#     name="X-API-Key",
#     auto_error=False
# )

# def verify_api_key(api_key: str = Security(api_key_header)):

#     key_map = {
#         API_KEY: "owner",
#         DEMO_API_KEY: "recruiter"
#     }

#     if api_key not in key_map:
#         raise HTTPException(
#             status_code=403,
#             detail="Invalid API Key"
#         )

#     return key_map[api_key]

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
# def insert_prediction(current_players, predicted, delta, status):
#     query = """
#         INSERT INTO player_predictions (
#             prediction_time,
#             current_players,
#             predicted_next_hour,
#             delta,
#             data_status
#         )
#         VALUES (NOW(), %s, %s, %s, %s)
#     """

#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute(query, (current_players, predicted, delta, status))

#     conn.commit()
#     cur.close()
#     conn.close()




DATABASE_URL = os.getenv("DATABASE_URL")

#engine = create_engine(DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

# from fastapi import FastAPI, HTTPException, Request, Security
# from fastapi.responses import JSONResponse
# from fastapi.security import APIKeyHeader
# import joblib
# import pandas as pd
# import numpy as np
# from pydantic import BaseModel
# from typing import List
# import os
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from slowapi.middleware import SlowAPIMiddleware
# from cachetools import TTLCache
# from pydantic import BaseModel
# from sqlalchemy import create_engine, text
# import os

@app.middleware("http")
async def log_requests(request: Request, call_next):

    client_ip = request.headers.get(
        "X-Forwarded-For",
        str(request.client.host)
    ).split(",")[0].strip()

    
     
    print(f"CLIENT IP: {client_ip}")
    print(f"FAILED ATTEMPTS: {FAILED_ATTEMPTS}")
    print(f"BLOCKED IPS: {BLOCKED_IPS}")
    
    protected_paths = [
        "/health",
        "/predict-live",
        "/major-order-status",
        "/forecast-24h",
        "/top-planets",
        "/forecast-vs-actual",
        "/total-players",
        "/faction-summary"
    ]
    
    path = request.url.path

    api_key = request.headers.get("X-API-Key")

    valid_keys = [
        API_KEY,
        DEMO_API_KEY
    ]

    is_protected = path in protected_paths
    is_valid_key = api_key in valid_keys
    # =========================
    # CHECK BLOCK
    # =========================
    if client_ip in BLOCKED_IPS:

        unblock_time = BLOCKED_IPS[client_ip]

        if time.time() < unblock_time:

            return JSONResponse(
                status_code=403,
                content={
                    "error": "Temporarily blocked"
                }
            )

        else:
            del BLOCKED_IPS[client_ip]
            FAILED_ATTEMPTS[client_ip] = 0
    
    
        # =========================
    # EARLY AUTH REJECTION
    # =========================
    if is_protected and not is_valid_key:

        FAILED_ATTEMPTS[client_ip] += 1

        print(f"FAILED LOGIN: {client_ip}")
        print(f"ATTEMPTS: {FAILED_ATTEMPTS[client_ip]}")

        if FAILED_ATTEMPTS[client_ip] >= MAX_FAILED_ATTEMPTS:

            BLOCKED_IPS[client_ip] = (
                time.time() + BLOCK_DURATION_SECONDS
            )

            print(f"BLOCKED IP: {client_ip}")

        return JSONResponse(
            status_code=403,
            content={
                "error": "Invalid API Key"
            }
        )
    
    response = await call_next(request)

    try:

        # =========================
        # SESSION ID
        # =========================
        session_id = request.headers.get("X-Session-ID")

        if not session_id:
            #session_id = str(request.client.host)
            session_id = client_ip

        # =========================
        # API KEY
        # =========================
        api_key = request.headers.get("X-API-Key")

        if api_key == API_KEY:
            user_type = "owner"

        elif api_key == DEMO_API_KEY:
            user_type = "recruiter"

        else:
            user_type = "anonymous"
            
        # =========================
        # RESET FAILED ATTEMPTS
        # ON SUCCESSFUL AUTH
        # =========================
        if user_type != "anonymous":
            FAILED_ATTEMPTS[client_ip] = 0

        # =========================
        # PATH
        # =========================
        path = request.url.path

        if path == "/":
            path = "/home"

        ignored_paths = [
            "/openapi.json",
            "/favicon.ico"
        ]

        if path in ignored_paths:
            return response

        # =========================
        # EVENT TYPE
        # =========================
        status_code = response.status_code

        if status_code == 403:
            event_type = "unauthorized"

        elif status_code == 429:
            event_type = "rate_limited"

        elif path == "/docs":
            event_type = "swagger_open"

        else:
            event_type = "api_call"
            
        # =========================
        # FAILED AUTH TRACKING
        # =========================
        # if user_type == "anonymous":
        # protected_paths = [
        #     "/health",
        #     "/predict-live",
        #     "/major-order-status",
        #     "/forecast-24h",
        #     "/top-planets",
        #     "/forecast-vs-actual",
        #     "/total-players"
        # ]

        # if (
        #     user_type == "anonymous"
        #     and path in protected_paths
        # ):

            # FAILED_ATTEMPTS[client_ip] += 1

            # print(f"FAILED LOGIN: {client_ip}")
            # print(f"ATTEMPTS: {FAILED_ATTEMPTS[client_ip]}")

            # if FAILED_ATTEMPTS[client_ip] >= MAX_FAILED_ATTEMPTS:

            #     BLOCKED_IPS[client_ip] = (
            #         time.time() + BLOCK_DURATION_SECONDS
            #     )

            #     print(f"BLOCKED IP: {client_ip}")

        # else:
        #     FAILED_ATTEMPTS[client_ip] = 0

        # =========================
        # INSERT
        # =========================
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO user_events (
                    session_id,
                    user_type,
                    event_type,
                    element
                )
                VALUES (
                    :session_id,
                    :user_type,
                    :event_type,
                    :element
                )
            """), {
                "session_id": session_id,
                "user_type": user_type,
                "event_type": event_type,
                "element": path
            })

    except Exception as e:
        print(f"Tracking middleware failed: {e}")

    return response

def fetch_recent_data(limit=500):
    limit = min(max(limit, 1), 1000)
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

@app.get("/health", tags=["System"], summary="API Health Check",

    description="""
Returns current API health information including:
- database connectivity
- model loading status
- latest available timestamp
- possible data integrity warnings

Useful for deployment monitoring and uptime validation.
""")

@limiter.limit("5/minute")
def health( request: Request,
    user_type: str = Security(verify_api_key)):

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


@app.get("/predict-live",
         
    tags=["Forecasting"],

    summary="Live Player Forecast Prediction",

    description="""
Generates a live forecast for upcoming Helldivers 2 player activity
using the latest available telemetry data.

This endpoint performs real-time feature engineering using:
- lag variables
- rolling statistics
- cyclical hour encoding
- Major Order participation metrics
- combat activity indicators

The prediction pipeline uses an XGBoost time-series forecasting model
trained on historical player engagement data stored in PostgreSQL.

Features:
- real-time inference
- quality threshold validation
- automatic stale-data detection
- latest timestamp monitoring

Use Cases:
- live engagement forecasting
- event impact monitoring
- player trend analysis
- dashboard integration
- model validation

Returns:
- predicted player counts
- forecast timestamps
- latest data timestamp
- server health information
- data quality indicators
"""
)
@limiter.limit("2/minute")
def predict_live( request: Request, user_type: str = Security(verify_api_key)):

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

@app.get("/major-order-status",tags=["Major Orders"], summary="Current Major Order Analytics",

    description="""
Returns real-time Major Order participation metrics.

Includes:
- players participating in Major Orders
- players outside Major Orders
- Major Order ratio
- current dispatch information

Used by the Streamlit analytics dashboard.
""")
@limiter.limit("3/minute")
def major_order_status( request: Request, user_type: str = Security(verify_api_key)):

    if "major_order_status" in major_order_cache:
        return major_order_cache["major_order_status"]
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

    # # -------------------------
    # # RESPONSE
    # # -------------------------
    # return {
    # "server_health": {
    #     "status": status,
    #     "warning": (
    #         "Current data likely incomplete due to missing planets/API issues"
    #         if status == "likely_missing_planets"
    #         else None
    #     )
    # },

    # "major_order_data": {
    #     "timestamp": str(latest["timestamp"]),

    #     "major_order_id": (
    #         int(latest["major_order_id"])
    #         if pd.notna(latest["major_order_id"])
    #         else None
    #     ),

    #     "major_order_dispatch": latest["major_order_dispatch"],

    #     "players_in_major_order": int(players_in),
    #     "players_outside_major_order": int(players_out),
    #     "total_players": int(total_players),

    #     "major_order_ratio": round(float(mo_ratio), 3)
    # }
    
    # -------------------------
# RESPONSE
# -------------------------
    result = {
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

    major_order_cache["major_order_status"] = result

    return result

    
@app.get("/major-order-history-by-day", tags=["Major Orders"], summary="Major Order History by Day")
@limiter.limit("3/minute")
def major_order_history_by_day( request: Request, days_ago: int = 5,
    user_type: str = Security(verify_api_key)):
    
    
    days_ago = min(max(days_ago, 1), 30)
    
    cache_key = f"major_order_history_{days_ago}"

    if cache_key in major_order_history_cache:
        return major_order_history_cache[cache_key]
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

    # return {
    #     "query_days_ago": days_ago,

    #     "major_order_id": int(target_major_order_id),

    #     "major_order_dispatch": dispatch,

    #     "history": history
    # }
    
    result = {
    "major_order_history": history
    }

    major_order_history_cache[cache_key] = result

    return result
    
    
@app.get("/forecast-24h",
         
    tags=["Forecasting"],

    summary="24-Hour Player Forecast",

    description="""
Forecasts Helldivers 2 total player counts over the next 24 hours.

This endpoint uses engineered time-series features including:
- lag variables
- rolling statistics
- cyclic hour encoding
- Major Order participation ratios

Model:
- XGBoost Regressor

Use Cases:
- engagement forecasting
- event impact analysis
- player trend monitoring
"""
)
@limiter.limit("2/minute")
def forecast_24h( request: Request, user_type: str = Security(verify_api_key)):
    
    if "forecast_24h" in forecast_cache:
        return forecast_cache["forecast_24h"]
    
    
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
    # row = df.iloc[0]
    
    # result = {
    #     "timestamp": str(row["timestamp"]),
    #     "total_players": total_players
    # }
    
    result = {
    "server_health": {
        "status": status
    },

    "forecast_horizon_hours": 24,

    "forecast": forecasts
    }

    forecast_cache["forecast_24h"] = result

    return result
    # return {
    #     "server_health": {
    #         "status": status
    #     },

    #     "forecast_horizon_hours": 24,

    #     "forecast": forecasts
    # }
    
    forecast_cache["forecast_24h"] = result

    return result
    
    
@app.get("/top-planets",
         
     tags=["Planets"],

    summary="Top Active Planets",

    description="""
Returns the planets with the highest active player counts.

Includes:
- planet names
- player totals
- faction ownership
- Major Order participation indicators
""")
@limiter.limit("3/minute")
def top_planets( request: Request,limit: int = 10,
    user_type: str = Security(verify_api_key)):
    limit = min(max(limit, 1), 50)
    cache_key = f"top_planets_{limit}"

    if cache_key in top_planets_cache:
        return top_planets_cache[cache_key]
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
            "strategic_opportunity": row["strategic_opportunity"],
            "possible_paths_to_major_order": (
        "T"
        if bool(row["possible_paths_to_major_order"])
        else "F"
        )   
        })

    # return {
    #     "server_health": {
    #         "status": status
    #     },

    #     "top_planets": planets
    # }
    result = {
    "server_health": {
        "status": status
    },

    "top_planets": planets
    }

    top_planets_cache[cache_key] = result

    return result

@app.get("/faction-summary",
         
     tags=["Factions"],

    summary="Current Faction Engagement",

    description="""
Summarizes current player distribution across enemy factions.

Useful for understanding:
- current war focus
- faction popularity
- real-time engagement shifts
""")
@limiter.limit("30/minute")
def faction_summary( request: Request, user_type: str = Security(verify_api_key)):
    #check the cache before hitting the database
    if "faction_summary" in summary_cache:
        return summary_cache["faction_summary"]
    
    query = """
    SELECT
        CASE

            -- HUMAN DEFENSE PLANETS
            WHEN "currentOwner" = 'Humans'
                 AND enemy_attacking_owner IS NOT NULL
                 AND enemy_attacking_owner != 'Humans'

            THEN enemy_attacking_owner

            -- ENEMY-OWNED LIBERATION PLANETS
            WHEN "currentOwner" != 'Humans'

            THEN "currentOwner"

        END AS enemy_faction,

        SUM(player_on_planet) AS total_players

    FROM planet_history

    WHERE timestamp = (
        SELECT MAX(timestamp)
        FROM planet_history
    )

    AND (
        (
            "currentOwner" = 'Humans'
            AND enemy_attacking_owner IS NOT NULL
            AND enemy_attacking_owner != 'Humans'
        )

        OR

        (
            "currentOwner" != 'Humans'
        )
    )

    GROUP BY enemy_faction

    ORDER BY total_players DESC
"""

    df = pd.read_sql(query, engine)

    # status = detect_data_issue(
    #     df.rename(columns={
    #         "total_players": "total_players"
    #     })
    # )
    
    status = "ok"

    factions = []

    for _, row in df.iterrows():

        # factions.append({
        #     "faction": row["currentOwner"],
        #     "players": int(row["total_players"])
        # })
        
        factions.append({
        "enemy_faction": row["enemy_faction"],
            "players_fighting": int(row["total_players"])
        })

    result = {
        "server_health": {
            "status": status
        },

        "factions": factions
    }
    #store into cache before returning
    summary_cache["faction_summary"] = result

    return result
    # return {
    #     "server_health": {
    #         "status": status
    #     },

    #     "factions": factions
    # }
    
    
@app.get("/forecast-vs-actual",
         
    tags=["Forecasting"],

    summary="Forecast vs Actual Comparison",

    description="""
Compares model predictions against real observed player counts.

Useful for:
- model evaluation
- forecast validation
- identifying underfitting during major events
""")
@limiter.limit("2/minute")
def forecast_vs_actual( request: Request, history_hours: int = 24, user_type: str = Security(verify_api_key)):
    cache_key = f"forecast_vs_actual_{history_hours}"

    if cache_key in forecast_vs_actual_cache:
        return forecast_vs_actual_cache[cache_key]
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
    # return {
    #     "server_health": {
    #         "status": status
    #     },

    #     "data": actuals + forecasts
    # }
    
    result = {
    "server_health": {
        "status": status
    },

    "forecast_vs_actual": actuals + forecasts
    }

    forecast_vs_actual_cache[cache_key] = result

    return result
    
@app.get("/total-players", tags=["Analytics"], summary="Get Total Player Count")
@limiter.limit("5/minute")
def total_players( request: Request,
    user_type: str = Security(verify_api_key)):

    if "total_players" in total_players_cache:
        return total_players_cache["total_players"]
    query = """
        SELECT
            timestamp,
            SUM(player_on_planet) AS total_players
        FROM planet_history
        WHERE timestamp = (
            SELECT MAX(timestamp)
            FROM planet_history
        )
        GROUP BY timestamp
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {
            "error": "No data found"
        }

    row = df.iloc[0]

    total_players = int(row["total_players"])

    # return {
    #     "timestamp": str(row["timestamp"]),
    #     "total_players": total_players
    # }
    result = {
    "timestamp": str(row["timestamp"]),
    "total_players": total_players
    }

    total_players_cache["total_players"] = result

    return result

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
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    print(f"Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)