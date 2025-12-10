# src/build_processed.py

import sys
from pathlib import Path

# Ensure project root visibility for imports when script runs directly
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import INDICATOR_CONFIG, DATA_PROCESSED_DIR
from src.cleaner import clean_and_save_indicator
from src.metadata import build_metadata


def main() -> None:
    print("🧹 Cleaning and standardizing indicators to monthly...\n")

    # Create processed folder if not present
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for indicator_id in INDICATOR_CONFIG.keys():
        try:
            df = clean_and_save_indicator(indicator_id)
            if df.empty:
                print(f" ⚠ {indicator_id}: EMPTY after cleaning — check raw data.")
            else:
                start = df["Date"].min().strftime("%Y-%m")
                end = df["Date"].max().strftime("%Y-%m")
                print(f" ✔ {indicator_id}: {len(df)} rows [{start} → {end}]")
        except Exception as e:
            print(f" ❌ ERROR processing {indicator_id}: {e}")

    print("\n📌 Building metadata...")
    meta_df = build_metadata()
    print(meta_df)
    print("\n🎯 Done! All indicators ready.\n")


if __name__ == "__main__":
    main()
