# import os
# import pandas as pd
# import psycopg2
# import logging

# from .config import PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
# def get_connection():
#     return psycopg2.connect(
#         host=PGHOST,
#         port=PGPORT,
#         database=PGDATABASE,
#         user=PGUSER,
#         password=PGPASSWORD,
#         sslmode="require"
#     )

# def fetch_new_data(latest_ts):
#     conn = get_connection()

#     try:
#         if latest_ts is None:
#             logging.info("First run: pulling initial dataset")
#             query = """
#                 SELECT *
#                 FROM planet_history
#                 ORDER BY timestamp
#                 LIMIT 500000
#             """
#         else:
#             logging.info(f"Fetching rows after {latest_ts}")
#             query = """
#                 SELECT *
#                 FROM planet_history
#                 WHERE timestamp > %s
#                 ORDER BY timestamp
#                 LIMIT 100000
#             """

#         if latest_ts is None:
#             df = pd.read_sql(query, conn)
#         else:
#             df = pd.read_sql(query, conn, params=(latest_ts,))

#         if not df.empty:
#             df["timestamp"] = pd.to_datetime(df["timestamp"])

#         logging.info(f"Fetched {len(df)} rows")
#         return df

#     finally:
#         conn.close()

import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))
    
def fetch_new_data(latest_ts):
    engine = get_engine()

    if latest_ts is None:
        query = """
            SELECT *
            FROM planet_history
            ORDER BY timestamp
            LIMIT 500000
        """
    else:
        query = f"""
            SELECT *
            FROM planet_history
            WHERE timestamp > '{latest_ts}'
            ORDER BY timestamp
        """

    df = pd.read_sql(query, engine)
    return df