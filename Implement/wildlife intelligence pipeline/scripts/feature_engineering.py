import pandas as pd
import logging

logger = logging.getLogger(__name__)


def add_size_category(df: pd.DataFrame) -> pd.DataFrame:
    """Add Size Category based on Weight (kg)."""
    if "Weight (kg)" not in df.columns:
        df["Size Category"] = "Unknown"
        return df

    def categorize_size(weight):
        if pd.isna(weight):
            return "Unknown"
        if weight < 10:
            return "Small"
        elif weight <= 100:
            return "Medium"
        else:
            return "Large"

    df["Size Category"] = df["Weight (kg)"].apply(categorize_size)
    return df


def add_speed_category(df: pd.DataFrame) -> pd.DataFrame:
    """Add Speed Category based on Top Speed (km/h)."""
    if "Top Speed (km/h)" not in df.columns:
        df["Speed Category"] = "Unknown"
        return df

    def categorize_speed(speed):
        if pd.isna(speed):
            return "Unknown"
        if speed < 30:
            return "Slow"
        elif speed <= 60:
            return "Medium"
        else:
            return "Fast"

    df["Speed Category"] = df["Top Speed (km/h)"].apply(categorize_speed)
    return df


def run_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all feature engineering steps."""
    df = add_size_category(df)
    df = add_speed_category(df)
    logger.info("Feature engineering complete: Size Category and Speed Category added.")
    return df
