# src/cleaner.py
from typing import Literal

import pandas as pd

from .config import DATA_PROCESSED_DIR, INDICATOR_CONFIG
from .loader import load_raw_indicator


def _infer_frequency(df: pd.DataFrame) -> Literal["daily", "monthly", "other"]:
    """
    Infer if the series is daily or monthly based on median date difference.
    Very rough, but enough for our context.
    """
    if len(df) < 3:
        return "other"

    diffs = df["Date"].diff().dropna().dt.days
    median_diff = diffs.median()

    if median_diff <= 10:
        return "daily"
    elif 25 <= median_diff <= 35:
        return "monthly"
    else:
        return "other"


def standardize_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce monthly data using month-end index.
    - If already monthly, just normalize to month end.
    - If daily, resample to month end using last observed value.
    """
    df = df.copy()
    df.set_index("Date", inplace=True)

    freq_type = _infer_frequency(df.reset_index())

    if freq_type == "daily":
        # Use last value in each month (financially sensible)
        monthly = df.resample("M").last()
    elif freq_type == "monthly":
        # Some series might be first-of-month; align to month end
        monthly = df.resample("M").last()
    else:
        # Default: try monthly resample anyway
        monthly = df.resample("M").last()

    monthly = monthly.dropna(subset=["Value"])

    monthly = monthly.reset_index()
    monthly = monthly.sort_values("Date").reset_index(drop=True)

    return monthly


def clean_and_save_indicator(indicator_id: str) -> pd.DataFrame:
    """
    Load raw, standardize to monthly, and save cleaned data to data_processed/.
    Returns cleaned DataFrame.
    """
    df_raw = load_raw_indicator(indicator_id)
    df_monthly = standardize_to_monthly(df_raw)

    # Ensure output directory exists
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    out_path = DATA_PROCESSED_DIR / f"{indicator_id}.csv"
    df_monthly.to_csv(out_path, index=False)

    return df_monthly
