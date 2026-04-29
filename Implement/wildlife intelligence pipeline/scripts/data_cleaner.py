import pandas as pd
import logging

logger = logging.getLogger(__name__)

NUMERIC_COLS = ["Height (cm)", "Weight (kg)", "Lifespan (years)",
                "Average Speed (km/h)", "Top Speed (km/h)",
                "Gestation Period (days)", "Offspring per Birth"]

TEXT_COLS = ["Animal", "Color", "Diet", "Habitat", "Predators",
             "Countries Found", "Conservation Status", "Family",
             "Social Structure"]


def _extract_numeric_mean(value):
    """For range strings like '40-65', return the mean as float."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    if "-" in s:
        parts = s.split("-")
        try:
            nums = [float(p.strip().replace(",", "")) for p in parts if p.strip()]
            return sum(nums) / len(nums)
        except ValueError:
            pass
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply full cleaning pipeline:
    - Strip whitespace from text columns
    - Standardize text (title-case Animal names)
    - Convert numeric columns (handling ranges)
    - Drop rows with null Animal
    """
    df = df.copy()

    # Strip whitespace from all object columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("nan", pd.NA)

    # Standardize Animal names
    if "Animal" in df.columns:
        df["Animal"] = df["Animal"].str.strip().str.title()

    # Convert numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].apply(_extract_numeric_mean)

    # Drop rows with no animal name
    if "Animal" in df.columns:
        df = df.dropna(subset=["Animal"])
        df = df[df["Animal"].str.strip() != ""]

    logger.info(f"Cleaned dataframe: {len(df)} rows remaining.")
    return df
