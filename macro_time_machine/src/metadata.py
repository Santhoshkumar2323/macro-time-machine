# src/metadata.py
from datetime import datetime

import pandas as pd

from .config import DATA_PROCESSED_DIR, METADATA_CSV_PATH, INDICATOR_CONFIG


def build_metadata() -> pd.DataFrame:
    """
    Scan all processed indicator CSVs and build a metadata table:
    indicator_id, display, country, category, start, end, rows
    """
    rows = []

    for indicator_id, info in INDICATOR_CONFIG.items():
        processed_path = DATA_PROCESSED_DIR / f"{indicator_id}.csv"
        if not processed_path.exists():
            # It might not be cleaned yet; skip silently.
            continue

        df = pd.read_csv(processed_path, parse_dates=["Date"])
        if df.empty:
            continue

        start_date = df["Date"].min()
        end_date = df["Date"].max()
        n_rows = len(df)

        rows.append(
            {
                "indicator_id": indicator_id,
                "display": info["display"],
                "country": info["country"],
                "category": info["category"],
                "start": start_date.strftime("%Y-%m"),
                "end": end_date.strftime("%Y-%m"),
                "rows": n_rows,
            }
        )

    meta_df = pd.DataFrame(rows).sort_values(["country", "category", "indicator_id"])

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    meta_df.to_csv(METADATA_CSV_PATH, index=False)

    return meta_df
