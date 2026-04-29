import os
import logging
import pandas as pd
from datetime import datetime

# Resolve paths relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_PATH = os.path.join(BASE_DIR, "data", "master", "animals_master.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")
LOG_PATH = os.path.join(BASE_DIR, "logs", "pipeline.log")

# Setup logging
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Import pipeline modules (safe for Streamlit re-runs)
import sys
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
from data_cleaner import clean_dataframe
from feature_engineering import run_feature_engineering


def read_csv_safe(path: str) -> pd.DataFrame | None:
    """Read a CSV, return None if it doesn't exist or is empty."""
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        if df.empty:
            return None
        return df
    except Exception as e:
        logger.warning(f"Could not read {path}: {e}")
        return None


def run_pipeline(uploaded_path: str | None = None) -> pd.DataFrame:
    """
    Full pipeline:
    1. Read master dataset
    2. Read uploaded dataset (if any)
    3. Merge & deduplicate
    4. Clean
    5. Feature engineering
    6. Save processed output
    7. Return final dataframe
    """
    logger.info("=== Pipeline started ===")

    # Step 1: Read master
    master_df = read_csv_safe(MASTER_PATH)
    if master_df is None:
        logger.warning("Master dataset is empty or missing.")
        master_df = pd.DataFrame()

    logger.info(f"Master rows: {len(master_df)}")

    # Step 2: Read uploaded
    upload_df = None
    if uploaded_path:
        upload_df = read_csv_safe(uploaded_path)
        if upload_df is not None:
            logger.info(f"Uploaded rows: {len(upload_df)}")

    # Step 3: Merge
    if upload_df is not None and not upload_df.empty:
        combined = pd.concat([master_df, upload_df], ignore_index=True)
        logger.info(f"Combined rows before dedup: {len(combined)}")
    else:
        combined = master_df.copy()

    if combined.empty:
        logger.error("No data to process.")
        return pd.DataFrame()

    # Step 4: Remove duplicates
    if "Animal" in combined.columns:
        before = len(combined)
        combined = combined.drop_duplicates(subset=["Animal"], keep="first")
        logger.info(f"Deduplication: {before} → {len(combined)} rows")

    # Step 5: Clean
    cleaned = clean_dataframe(combined)

    # Step 6: Feature engineering
    final = run_feature_engineering(cleaned)

    # Step 7: Save
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    final.to_csv(PROCESSED_PATH, index=False)

    # Also update master with merged deduplicated raw data
    if upload_df is not None and not upload_df.empty:
        os.makedirs(os.path.dirname(MASTER_PATH), exist_ok=True)
        combined_raw = pd.concat([master_df, upload_df], ignore_index=True)
        if "Animal" in combined_raw.columns:
            combined_raw = combined_raw.drop_duplicates(subset=["Animal"], keep="first")
        combined_raw.to_csv(MASTER_PATH, index=False)
        logger.info("Master dataset updated.")

    logger.info(f"Pipeline complete. Final rows: {len(final)}")
    return final


def load_processed() -> pd.DataFrame:
    """Load the processed clean data if available."""
    df = read_csv_safe(PROCESSED_PATH)
    if df is None:
        # Run pipeline without upload to generate it
        df = run_pipeline()
    return df if df is not None else pd.DataFrame()
