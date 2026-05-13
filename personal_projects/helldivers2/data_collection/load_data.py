
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pathlib import Path

from dotenv import load_dotenv

# ✅ load env (auto-find)
load_dotenv()

# ✅ base directory of this file
BASE_DIR = Path(__file__).resolve().parent

# ✅ data path
DATA_PATH = BASE_DIR / "data" / "planet_history.parquet"

# 🔧 config: how fresh is "fresh"
MAX_AGE_MINUTES = 60


def get_engine():
    database_url = os.getenv("DATABASE_URL")
    #print(os.getenv("DATABASE_URL"))
    if not database_url:
        raise ValueError("DATABASE_URL not set")

    return create_engine(database_url)


def is_data_stale():
    if not DATA_PATH.exists():
        return True

    last_modified = datetime.fromtimestamp(DATA_PATH.stat().st_mtime)
    age = datetime.now() - last_modified

    return age > timedelta(minutes=MAX_AGE_MINUTES)


def load_data(force_db=False):
    # 🔥 decide whether to refresh
    if force_db or is_data_stale():
        print("🔄 Refreshing data from DB...")

        engine = get_engine()
        df = pd.read_sql("SELECT * FROM planet_history", engine)

        # 💾 update cache
        DATA_PATH.parent.mkdir(exist_ok=True)
        df.to_parquet(DATA_PATH, index=False)

        return df

    # ⚡ fast path
    print("⚡ Loading from parquet cache")
    return pd.read_parquet(DATA_PATH)