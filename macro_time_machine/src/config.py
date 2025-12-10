# src/config.py
from pathlib import Path

# Base directory: the project root (where you run Python from)
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_RAW_DIR = BASE_DIR / "data_raw"
DATA_PROCESSED_DIR = BASE_DIR / "data_processed"
METADATA_CSV_PATH = DATA_PROCESSED_DIR / "indicators_meta.csv"


# Mapping from logical indicator_id -> file + display info.
# You can adjust names later, but this is a solid starting point.
INDICATOR_CONFIG = {
    "fed_funds": {
        "file": "fed_funds.csv",
        "country": "US",
        "category": "Interest Rates",
        "display": "US: Fed Funds Rate",
    },
    "us_cpi": {
        "file": "us_cpi.csv",
        "country": "US",
        "category": "Inflation",
        "display": "US: CPI Inflation",
    },
    "us_10y": {
        "file": "us_10y.csv",
        "country": "US",
        "category": "Bond Market",
        "display": "US: 10Y Treasury Yield",
    },
    "us_yield_curve_10y_2y": {
        "file": "T10Y2Y (1).csv",   # full history file
        "country": "US",
        "category": "Stress Indicator",
        "display": "US: 10Y–2Y Yield Curve",
    },
    "us_hy_spread": {
        "file": "BAMLH0A0HYM2.csv",
        "country": "US",
        "category": "Credit Spread",
        "display": "US: High Yield Spread (BAML)",
    },
    "vix": {
        "file": "vix.csv",
        "country": "US",
        "category": "Market Volatility",
        "display": "US: VIX Index",
    },
    "crude_oil": {
        "file": "crude_oil.csv",
        "country": "Global",
        "category": "Commodities",
        "display": "Crude Oil Price",
    },
    "dxy": {
        "file": "dxy.csv",
        "country": "US",
        "category": "Currencies",
        "display": "US Dollar Index (DXY)",
    },
    "in_fx_spot": {
        "file": "in_fx_spot.csv",
        "country": "India",
        "category": "Currencies",
        "display": "INR/USD FX Spot",
    },
    "in_policy_rate": {
        "file": "in_policy_rate.csv",
        "country": "India",
        "category": "Interest Rates",
        "display": "India: Policy Repo Rate",
    },
    "in_cpi": {
        "file": "in_cpi.csv",
        "country": "India",
        "category": "Inflation",
        "display": "India: CPI Inflation",
    },
    "in_m3": {
        "file": "in_m3.csv",
        "country": "India",
        "category": "Money Supply",
        "display": "India: M3 Money Supply",
    },
    "in_production": {
        "file": "in_production.csv",
        "country": "India",
        "category": "Growth",
        "display": "India: Industrial Production",
    },
}
