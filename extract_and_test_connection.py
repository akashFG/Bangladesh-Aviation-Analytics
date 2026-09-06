"""
ETL Pipeline - Step 1: Extract / Stage raw data (local, no cloud storage cost)
Instead of AWS S3, this stages raw CSVs into a local 'raw/' folder to
simulate a landing zone, then verifies connectivity to the Supabase
(cloud PostgreSQL) database that will hold the final data mart.
"""

import os
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()  # reads .env file

SOURCE_DIR = "."  # current folder (this script sits next to the CSVs)
STAGING_ROOT = "./pipeline_data/raw"

FILES_TO_STAGE = [
    "bd_flights_2024.csv",
    "dim_airlines.csv",
    "dim_airports.csv",
    "dim_routes.csv",
]


def stage_raw_files():
    """Copy source CSVs into a dated 'raw/' landing folder (mimics S3 landing zone)."""
    run_date = datetime.utcnow().strftime("%Y-%m-%d")
    dest_dir = os.path.join(STAGING_ROOT, run_date)
    os.makedirs(dest_dir, exist_ok=True)

    staged = 0
    for filename in FILES_TO_STAGE:
        src = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(src):
            logger.warning(f"Missing source file, skipping: {src}")
            continue
        dst = os.path.join(dest_dir, filename)
        shutil.copy2(src, dst)
        logger.info(f"Staged {filename} -> {dst}")
        staged += 1

    logger.info(f"Staging complete: {staged}/{len(FILES_TO_STAGE)} files -> {dest_dir}")
    return dest_dir


def test_supabase_connection():
    """Verify we can reach the Supabase Postgres instance."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url or "[YOUR-PASSWORD]" in db_url:
        logger.error("SUPABASE_DB_URL not set correctly in .env file.")
        return False

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        logger.info(f"Connected to Supabase successfully. Postgres version: {version[0][:50]}...")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return False


if __name__ == "__main__":
    logger.info("=== Step 1: Extract / Stage raw data ===")
    stage_raw_files()

    logger.info("=== Testing Supabase connection ===")
    test_supabase_connection()