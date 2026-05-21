"""
pipeline/validator.py - Data Validation Pipeline
Wildlife Intelligence Monitoring System
"""
import logging
from dataclasses import dataclass, field
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class DataValidator:
    """
    Validates wildlife dataset before processing.
    Checks for required columns, data types, and business rules.
    """

    REQUIRED_COLUMNS = ["Animal"]  # Minimum required column
    EXPECTED_COLUMNS = [
        "Animal", "Height (cm)", "Weight (kg)", "Color", "Lifespan (years)",
        "Diet", "Habitat", "Predators", "Top Speed (km/h)", "Countries Found",
        "Conservation Status", "Social Structure", "Offspring per Birth",
    ]
    VALID_CONSERVATION_STATUSES = {
        "Least Concern", "Near Threatened", "Vulnerable",
        "Endangered", "Critically Endangered", "Extinct in the Wild",
        "Extinct", "Unknown",
    }

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Run all validation checks. Returns ValidationResult."""
        errors: List[str] = []
        warnings: List[str] = []

        # Check empty dataframe
        if df.empty:
            errors.append("Dataset is empty.")
            return ValidationResult(is_valid=False, errors=errors)

        # Required column check
        missing_required = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing_required:
            errors.append(f"Missing required columns: {missing_required}")

        # Expected column check (warnings only)
        missing_expected = [c for c in self.EXPECTED_COLUMNS if c not in df.columns]
        if missing_expected:
            warnings.append(f"Optional columns absent (will be set to N/A): {missing_expected}")

        # Null analysis
        null_pct = df.isnull().mean() * 100
        high_null_cols = null_pct[null_pct > 50].index.tolist()
        if high_null_cols:
            warnings.append(f"Columns with >50% nulls: {high_null_cols}")

        # Duplicate detection
        dup_count = df.duplicated(subset=["Animal"] if "Animal" in df.columns else None).sum()
        if dup_count > 0:
            warnings.append(f"Found {dup_count} duplicate rows (will be removed).")

        # Conservation status validation
        if "Conservation Status" in df.columns:
            unique_statuses = set(df["Conservation Status"].dropna().unique())
            invalid = unique_statuses - self.VALID_CONSERVATION_STATUSES - {""}
            if invalid:
                warnings.append(f"Non-standard conservation statuses found: {invalid}")

        # Speed range validation
        speed_col = "Top Speed (km/h)" if "Top Speed (km/h)" in df.columns else "Average Speed (km/h)"
        if speed_col in df.columns:
            numeric_speeds = pd.to_numeric(df[speed_col], errors="coerce")
            outliers = (numeric_speeds > 500).sum()
            if outliers > 0:
                warnings.append(f"{outliers} rows have suspicious speed > 500 km/h.")

        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "null_values": int(df.isnull().sum().sum()),
            "duplicate_rows": int(dup_count),
            "columns_found": list(df.columns),
        }

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=stats,
        )
