"""
End-to-end pipeline: load -> deduplicate -> clean -> export.
Produces the cleaned dataset as a CSV ready for Tableau or analysis.
Run with: python3 src/pipeline.py
"""

from pathlib import Path

from load_data import load_raw
from clean_data import build_cleaned

OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "fragrances_cleaned.csv"


def run() -> Path:
    df_raw = load_raw()
    df_clean = build_cleaned(df_raw)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_FILE, index=False)
    print(f"Exported {len(df_clean):,} rows -> {OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    run()