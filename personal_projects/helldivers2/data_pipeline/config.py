import os
from dotenv import load_dotenv

load_dotenv()

LOCAL_DATA_PATH = "data/planet_history.parquet"

PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

if None in [PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD]:
    raise ValueError("Missing one or more DB environment variables")