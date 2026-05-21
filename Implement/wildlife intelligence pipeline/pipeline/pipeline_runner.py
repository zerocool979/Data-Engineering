"""
pipeline/pipeline_runner.py - ETL Pipeline Orchestrator
Wildlife Intelligence Monitoring System

Orchestrates: Validate → Clean → Feature Engineer → Load to DB
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.cleaner import DataCleaner
from pipeline.validator import DataValidator
from pipeline.feature_engineering import FeatureEngineer
from backend.database.connection import get_session, init_db
from backend.database.models import Animal, Upload, PipelineLog

# Configure logging to file + console
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("pipeline_runner")


class PipelineRunner:
    """
    Main ETL pipeline orchestrator.
    Validates, cleans, engineers features, and loads data to SQLite.
    """

    def __init__(self):
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.engineer = FeatureEngineer()
        init_db()

    def run(self, df: pd.DataFrame, source_file: str = "unknown") -> dict:
        """
        Execute full ETL pipeline for a given dataframe.
        Returns a summary dict with metrics.
        """
        start_time = datetime.now()
        logger.info(f"=== Pipeline START: {source_file} ===")
        session = get_session()

        # Track upload record
        upload = Upload(filename=source_file, rows_total=len(df), status="pending")
        session.add(upload)
        session.commit()

        try:
            # Stage 1: Validate
            self._log_to_db(session, "validate", "INFO", f"Validating {len(df)} rows from {source_file}")
            validation = self.validator.validate(df)
            if not validation.is_valid:
                raise ValueError(f"Validation failed: {validation.errors}")

            for warning in validation.warnings:
                self._log_to_db(session, "validate", "WARNING", warning)

            # Stage 2: Clean
            self._log_to_db(session, "clean", "INFO", "Starting data cleaning...")
            df_clean = self.cleaner.clean(df, source_file=source_file)
            quality_report = self.cleaner.get_quality_report(df, df_clean)
            self._log_to_db(session, "clean", "INFO",
                            f"Cleaning done. Quality score={quality_report['quality_score']}")

            # Stage 3: Feature Engineering
            self._log_to_db(session, "feature_eng", "INFO", "Running feature engineering...")
            df_final = self.engineer.engineer(df_clean)
            self._log_to_db(session, "feature_eng", "INFO", "Feature engineering complete.")

            # Stage 4: Load to DB (anti-duplicate merge)
            inserted, skipped = self._load_to_db(session, df_final)
            self._log_to_db(session, "load", "INFO",
                            f"Loaded: inserted={inserted}, skipped(dup)={skipped}")

            # Update upload record
            upload.rows_inserted = inserted
            upload.rows_duplicate = skipped
            upload.rows_invalid = quality_report.get("null_values", 0)
            upload.quality_score = quality_report["quality_score"]
            upload.status = "success"
            session.commit()

            elapsed = (datetime.now() - start_time).total_seconds()
            summary = {
                "status": "success",
                "source": source_file,
                "rows_total": len(df),
                "rows_inserted": inserted,
                "rows_skipped": skipped,
                "quality_score": quality_report["quality_score"],
                "elapsed_seconds": round(elapsed, 2),
                "warnings": validation.warnings,
            }
            logger.info(f"=== Pipeline END: {summary} ===")
            return summary

        except Exception as e:
            upload.status = "failed"
            upload.error_message = str(e)
            session.commit()
            self._log_to_db(session, "error", "ERROR", str(e))
            logger.error(f"Pipeline FAILED: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}
        finally:
            session.close()

    def _load_to_db(self, session, df: pd.DataFrame) -> tuple[int, int]:
        """
        Load cleaned+engineered rows to the animals table.
        Skips animals that already exist (by name, case-insensitive).
        Returns (inserted_count, skipped_count).
        """
        # Get existing animal names for dedup
        existing = {
            r[0].lower()
            for r in session.query(Animal.name).all()
        }

        inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name or name.lower() == "unknown":
                continue

            if name.lower() in existing:
                skipped += 1
                continue

            animal = Animal(
                name=name,
                height_cm=row.get("height_cm"),
                weight_kg=row.get("weight_kg"),
                color=row.get("color"),
                lifespan_years=row.get("lifespan_years"),
                diet=row.get("diet"),
                habitat=row.get("habitat"),
                predators=row.get("predators"),
                top_speed_kmh=row.get("top_speed_kmh"),
                countries_found=row.get("countries_found"),
                conservation_status=row.get("conservation_status"),
                family=row.get("family"),
                gestation_period_days=row.get("gestation_period_days"),
                social_structure=row.get("social_structure"),
                offspring_per_birth=row.get("offspring_per_birth"),
                size_category=row.get("size_category"),
                speed_category=row.get("speed_category"),
                risk_score=row.get("risk_score"),
                endangered_level=row.get("endangered_level"),
                survival_probability=row.get("survival_probability"),
                source_file=row.get("source_file"),
            )
            session.add(animal)
            existing.add(name.lower())
            inserted += 1

        session.commit()
        return inserted, skipped

    def _log_to_db(self, session, stage: str, level: str, message: str):
        """Persist a pipeline log entry."""
        log = PipelineLog(pipeline_name="main_etl", stage=stage,
                          level=level, message=message)
        session.add(log)
        session.commit()


def run_initial_load():
    """Load all datasets from master + uploads directories on first run."""
    DATA_DIR = Path(__file__).parent.parent / "data"
    runner = PipelineRunner()
    results = []

    for csv_path in list((DATA_DIR / "master").glob("*.csv")) + list((DATA_DIR / "uploads").glob("*.csv")):
        try:
            df = pd.read_csv(csv_path)
            result = runner.run(df, source_file=csv_path.name)
            results.append(result)
            logger.info(f"Loaded {csv_path.name}: {result}")
        except Exception as e:
            logger.error(f"Failed to load {csv_path.name}: {e}")

    return results


if __name__ == "__main__":
    logger.info("Running initial data load...")
    results = run_initial_load()
    for r in results:
        print(r)
