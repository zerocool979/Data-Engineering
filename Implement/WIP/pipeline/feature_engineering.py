"""
pipeline/feature_engineering.py - Feature Engineering Pipeline
Wildlife Intelligence Monitoring System
"""
import logging
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Generates derived/engineered features from cleaned wildlife data.
    Adds risk scores, categories, and survival probability.
    """

    CONSERVATION_RISK = {
        "Least Concern": 1,
        "Near Threatened": 2,
        "Vulnerable": 3,
        "Endangered": 4,
        "Critically Endangered": 5,
        "Extinct in the Wild": 6,
        "Extinct": 7,
        "Unknown": 0,
    }

    def engineer(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run all feature engineering steps."""
        logger.info("Starting feature engineering...")
        df = df.copy()
        df = self._add_speed_category(df)
        df = self._add_size_category(df)
        df = self._add_endangered_level(df)
        df = self._add_risk_score(df)
        df = self._add_survival_probability(df)
        logger.info("Feature engineering complete.")
        return df

    def _add_speed_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize animals by top speed."""
        def categorize_speed(speed) -> str:
            if pd.isna(speed) or speed == 0:
                return "Unknown"
            speed = float(speed)
            if speed < 20:
                return "Slow"
            elif speed < 50:
                return "Moderate"
            elif speed < 80:
                return "Fast"
            else:
                return "Very Fast"

        if "top_speed_kmh" in df.columns:
            df["speed_category"] = df["top_speed_kmh"].apply(categorize_speed)
        else:
            df["speed_category"] = "Unknown"
        return df

    def _add_size_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Derive size category from weight_kg.
        Weight column may be a range string like '40-65'.
        """
        def parse_midpoint(val) -> Optional[float]:
            if val is None or str(val) in ("N/A", "Unknown", "nan"):
                return None
            s = str(val).replace(",", "").strip()
            if "-" in s:
                parts = s.split("-")
                try:
                    return (float(parts[0]) + float(parts[-1])) / 2
                except ValueError:
                    return None
            try:
                return float(s)
            except ValueError:
                return None

        def categorize_size(weight_mid) -> str:
            if weight_mid is None:
                return "Unknown"
            if weight_mid < 5:
                return "Tiny"
            elif weight_mid < 50:
                return "Small"
            elif weight_mid < 300:
                return "Medium"
            elif weight_mid < 2000:
                return "Large"
            else:
                return "Giant"

        if "weight_kg" in df.columns:
            weight_mids = df["weight_kg"].apply(parse_midpoint)
            df["size_category"] = weight_mids.apply(categorize_size)
        else:
            df["size_category"] = "Unknown"
        return df

    def _add_endangered_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map conservation status to numeric endangered level (0-7)."""
        if "conservation_status" in df.columns:
            df["endangered_level"] = df["conservation_status"].map(
                lambda x: self.CONSERVATION_RISK.get(str(x), 0)
            )
        else:
            df["endangered_level"] = 0
        return df

    def _add_risk_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Composite risk score 0-100.
        Higher = more at risk. Combines:
        - Endangered level (60% weight)
        - Speed (slow animals harder to escape = higher risk, 20% weight)
        - Size (larger animals = more habitat pressure, 20% weight)
        """
        def compute_risk(row) -> float:
            # Endangered component (0-60)
            endangered = row.get("endangered_level", 0) or 0
            endangered_score = (endangered / 7) * 60

            # Speed component (0-20): slower = higher risk
            speed = row.get("top_speed_kmh", 0) or 0
            max_speed = 120.0
            speed_score = max(0, (1 - speed / max_speed)) * 20

            # Size component (0-20): larger = higher pressure
            size_map = {"Tiny": 2, "Small": 5, "Medium": 10, "Large": 15, "Giant": 20, "Unknown": 5}
            size_score = size_map.get(str(row.get("size_category", "Unknown")), 5)

            return round(min(100, endangered_score + speed_score + size_score), 1)

        df["risk_score"] = df.apply(compute_risk, axis=1)
        return df

    def _add_survival_probability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Survival probability 0.0-1.0 (inverse of risk).
        Adjusted by social structure bonus.
        """
        social_bonus = {
            "Herd-Based": 0.05, "Group-Based": 0.04, "Pack": 0.04,
            "Group": 0.03, "Colonial": 0.03,
            "Solitary": -0.02, "Unknown": 0.0,
        }

        def compute_survival(row) -> float:
            risk = row.get("risk_score", 50) or 50
            base = round(1.0 - (risk / 100), 3)
            social = row.get("social_structure", "Unknown") or "Unknown"
            bonus = social_bonus.get(social.title(), 0.0)
            return round(max(0.01, min(0.99, base + bonus)), 3)

        df["survival_probability"] = df.apply(compute_survival, axis=1)
        return df
