"""
pipeline/cleaner.py - Data Cleaning Pipeline
Wildlife Intelligence Monitoring System
"""
import re
import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Handles all data cleaning operations for wildlife datasets.
    Supports range-string columns like "40-65" for weight/height.
    """

    # Canonical column mapping: maps raw CSV headers -> standard names
    COLUMN_MAP = {
        "Animal": "name",
        "Height (cm)": "height_cm",
        "Weight (kg)": "weight_kg",
        "Color": "color",
        "Lifespan (years)": "lifespan_years",
        "Diet": "diet",
        "Habitat": "habitat",
        "Predators": "predators",
        "Average Speed (km/h)": "avg_speed_kmh",
        "Top Speed (km/h)": "top_speed_kmh",
        "Countries Found": "countries_found",
        "Conservation Status": "conservation_status",
        "Family": "family",
        "Gestation Period (days)": "gestation_period_days",
        "Social Structure": "social_structure",
        "Offspring per Birth": "offspring_per_birth",
    }

    CONSERVATION_LEVELS = {
        "Least Concern": 1,
        "Near Threatened": 2,
        "Vulnerable": 3,
        "Endangered": 4,
        "Critically Endangered": 5,
        "Extinct in the Wild": 6,
        "Extinct": 7,
    }

    def clean(self, df: pd.DataFrame, source_file: str = "unknown") -> pd.DataFrame:
        """
        Run full cleaning pipeline on a dataframe.
        Returns cleaned dataframe with standardized columns.
        """
        logger.info(f"Starting cleaning pipeline for {source_file}, rows={len(df)}")

        df = df.copy()
        df = self._rename_columns(df)
        df = self._clean_whitespace(df)
        df = self._normalize_text(df)
        df = self._parse_speed(df)
        df = self._handle_nulls(df)
        df = self._remove_duplicates(df)
        df["source_file"] = source_file

        logger.info(f"Cleaning complete. Final rows={len(df)}")
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map raw column names to standard names."""
        rename = {k: v for k, v in self.COLUMN_MAP.items() if k in df.columns}
        df = df.rename(columns=rename)
        # Ensure all standard columns exist
        for col in self.COLUMN_MAP.values():
            if col not in df.columns:
                df[col] = None
        return df

    def _clean_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip leading/trailing whitespace from all string columns."""
        obj_cols = [c for c in df.columns if hasattr(df[c], "str")]
        for col in obj_cols:
            series = df[col].astype(str).str.strip()
            df[col] = series.where(~series.isin(["nan", "None", ""]), other=None)
        return df

    def _normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Title-case animal names, normalize conservation status."""
        if "name" in df.columns:
            df["name"] = df["name"].str.title()

        if "conservation_status" in df.columns:
            # Standardize common variations
            status_map = {
                "lc": "Least Concern",
                "nt": "Near Threatened",
                "vu": "Vulnerable",
                "en": "Endangered",
                "cr": "Critically Endangered",
                "ew": "Extinct in the Wild",
                "ex": "Extinct",
            }
            def normalize_status(val):
                if pd.isna(val) or val is None:
                    return "Unknown"
                v = str(val).strip().lower()
                return status_map.get(v, str(val).strip().title())

            df["conservation_status"] = df["conservation_status"].apply(normalize_status)

        if "diet" in df.columns:
            df["diet"] = df["diet"].str.title()

        if "social_structure" in df.columns:
            df["social_structure"] = df["social_structure"].str.title()

        return df

    def _parse_speed(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert speed columns - handle ranges like '24-30' -> midpoint."""
        # Parse avg speed if present
        avg_vals = None
        if "avg_speed_kmh" in df.columns:
            avg_vals = df["avg_speed_kmh"].apply(self._parse_numeric_range).reset_index(drop=True)
            df = df.drop(columns=["avg_speed_kmh"])

        # Parse top speed
        if "top_speed_kmh" in df.columns:
            top_vals = df["top_speed_kmh"].apply(self._parse_numeric_range).reset_index(drop=True)
            df = df.reset_index(drop=True)
            # Use top speed; fall back to avg if top is null
            if avg_vals is not None:
                df["top_speed_kmh"] = top_vals.where(top_vals.notna(), other=avg_vals)
            else:
                df["top_speed_kmh"] = top_vals
        elif avg_vals is not None:
            df = df.reset_index(drop=True)
            df["top_speed_kmh"] = avg_vals

        return df

    def _parse_numeric_range(self, val) -> Optional[float]:
        """Parse a value that may be a range '10-20' or a plain number."""
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return None
        s = str(val).strip().replace(",", "")
        # Range pattern: "24-30"
        range_match = re.match(r"^([\d.]+)\s*[-–]\s*([\d.]+)$", s)
        if range_match:
            lo, hi = float(range_match.group(1)), float(range_match.group(2))
            return round((lo + hi) / 2, 2)
        # Plain number
        try:
            return float(s)
        except (ValueError, TypeError):
            return None

    def _handle_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill or flag null values appropriately."""
        str_cols = ["name", "habitat", "diet", "color", "conservation_status",
                    "countries_found", "family", "social_structure",
                    "predators", "offspring_per_birth"]
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown")

        range_cols = ["height_cm", "weight_kg", "lifespan_years",
                      "gestation_period_days"]
        for col in range_cols:
            if col in df.columns:
                df[col] = df[col].fillna("N/A")

        if "top_speed_kmh" in df.columns:
            df["top_speed_kmh"] = df["top_speed_kmh"].fillna(0.0)

        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicate animal names (case-insensitive)."""
        if "name" in df.columns:
            df["_name_lower"] = df["name"].str.lower().str.strip()
            before = len(df)
            df = df.drop_duplicates(subset=["_name_lower"], keep="first")
            df = df.drop(columns=["_name_lower"])
            removed = before - len(df)
            if removed > 0:
                logger.warning(f"Removed {removed} duplicate animals")
        return df

    def get_quality_report(self, df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> dict:
        """Generate a data quality report comparing raw vs cleaned data."""
        total = len(df_raw)
        if total == 0:
            return {"quality_score": 0, "total_rows": 0}

        null_count = df_raw.isnull().sum().sum()
        dup_count = df_raw.duplicated().sum()
        clean_rows = len(df_clean)

        quality_score = max(0, 100 - (null_count / max(total * len(df_raw.columns), 1) * 50) - (dup_count / total * 30))
        quality_score = round(min(100, quality_score), 1)

        return {
            "total_rows_raw": total,
            "total_rows_clean": clean_rows,
            "null_values": int(null_count),
            "duplicates_removed": int(dup_count),
            "quality_score": quality_score,
        }
