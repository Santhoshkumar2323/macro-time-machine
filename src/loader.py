# src/loader.py
from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import DATA_RAW_DIR, INDICATOR_CONFIG


def _detect_date_and_value_columns(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Try to automatically detect date column and value column.
    Assumes:
      - exactly 2 columns: [date, value]   OR
      - one column containing 'date' and one numeric column.
    """
    cols = list(df.columns)

    # Fast path: typical FRED format: ['observation_date', 'SERIES']
    if len(cols) == 2:
        date_col, value_col = cols[0], cols[1]
        return date_col, value_col

    # Fallback: try to find date-like column
    date_candidates = [c for c in cols if "date" in c.lower()]
    if not date_candidates:
        raise ValueError(f"Could not find a date column in columns: {cols}")

    date_col = date_candidates[0]
    value_cols = [c for c in cols if c != date_col]

    if len(value_cols) != 1:
        raise ValueError(
            f"Expected exactly 1 value column, found {len(value_cols)}: {value_cols}"
        )

    return date_col, value_cols[0]


def load_raw_indicator(indicator_id: str) -> pd.DataFrame:
    """
    Load the raw CSV for a given indicator_id, return a DataFrame
    with at least a date column and one numeric value column.
    """
    if indicator_id not in INDICATOR_CONFIG:
        raise KeyError(f"Unknown indicator_id: {indicator_id}")

    file_name = INDICATOR_CONFIG[indicator_id]["file"]
    csv_path = DATA_RAW_DIR / file_name

    if not csv_path.exists():
        raise FileNotFoundError(f"Raw CSV not found for {indicator_id}: {csv_path}")

    df = pd.read_csv(csv_path)

    date_col, value_col = _detect_date_and_value_columns(df)

    # Keep just those two columns
    df = df[[date_col, value_col]].copy()

    # Standardize column names
    df.rename(columns={date_col: "Date", value_col: "Value"}, inplace=True)

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Ensure Value is numeric
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    # Sort by date ascending
    df = df.sort_values("Date").reset_index(drop=True)

    return df
