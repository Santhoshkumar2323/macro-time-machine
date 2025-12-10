# src/slicer.py (updated with Change %)
from dataclasses import dataclass
from datetime import date
from typing import Optional, Literal, Dict, Any

import pandas as pd

from .config import DATA_PROCESSED_DIR


WindowType = Literal["1Y", "3Y", "5Y", "10Y", "20Y", "30Y"]


@dataclass
class SliceResult:
    indicator_id: str
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    data: pd.DataFrame
    summary: Dict[str, Any]


def _load_processed(indicator_id: str) -> pd.DataFrame:
    path = DATA_PROCESSED_DIR / f"{indicator_id}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Processed CSV not found: {path}")

    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def _apply_fixed_window(df: pd.DataFrame, window: WindowType) -> pd.DataFrame:
    last_date = df["Date"].max()
    years = int(window.replace("Y", ""))
    start_year = last_date.year - years
    start_candidate = pd.Timestamp(year=start_year, month=last_date.month, day=1)

    mask = (df["Date"] >= start_candidate) & (df["Date"] <= last_date)
    return df.loc[mask].copy()


def slice_indicator(
    indicator_id: str,
    *,
    window: Optional[WindowType] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> SliceResult:

    df = _load_processed(indicator_id)

    if window is not None and (start is not None or end is not None):
        raise ValueError("Use either 'window' OR ('start'/'end'), not both.")

    if window is not None:
        sliced = _apply_fixed_window(df, window)
    else:
        start_ts = pd.to_datetime(start + "-01") if start else df["Date"].min()
        end_ts = pd.to_datetime(end + "-01") + pd.offsets.MonthEnd(0) if end else df["Date"].max()
        mask = (df["Date"] >= start_ts) & (df["Date"] <= end_ts)
        sliced = df.loc[mask].copy()

    if sliced.empty:
        raise ValueError("Sliced data is empty for given parameters.")

    # Ensure sorted monthly data
    sliced = sliced.sort_values("Date").reset_index(drop=True)

    # ---- NEW FEATURE: Monthly Change % column ----
    sliced["Change %"] = sliced["Value"].pct_change() * 100

    # Clean formatting: first row & inf/nan cases → 0.00%
    sliced["Change %"] = sliced["Change %"].fillna(0.0)
    sliced["Change %"] = sliced["Change %"].replace([float("inf"), float("-inf")], 0.0)

    # Format to 2 decimals with % symbol
    sliced["Change %"] = sliced["Change %"].apply(lambda x: f"{x:.2f}%")

    # ----------------------------------------------------

    # Summary Stats (unchanged)
    start_val = sliced["Value"].iloc[0]
    end_val = sliced["Value"].iloc[-1]
    change = end_val - start_val
    pct_change = (change / start_val * 100) if start_val != 0 else None

    summary = {
        "start_value": float(start_val),
        "end_value": float(end_val),
        "abs_change": float(change),
        "pct_change": float(pct_change) if pct_change is not None else None,
        "min_value": float(sliced["Value"].min()),
        "max_value": float(sliced["Value"].max()),
        "avg_value": float(sliced["Value"].mean()),
        "rows": int(len(sliced)),
    }

    return SliceResult(
        indicator_id=indicator_id,
        start_date=sliced["Date"].min(),
        end_date=sliced["Date"].max(),
        data=sliced,
        summary=summary,
    )
