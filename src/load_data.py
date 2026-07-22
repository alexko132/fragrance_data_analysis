"""
Stage 1: Data acquisition and raw load.
Replaces 01_create_raw_table.sql and 02_import_data.sql.
Downloads the raw fragrance dataset (if missing) and loads it as a
string-typed DataFrame. Typing and cleaning happen in clean_data.py,
mirroring the raw-table -> cleaned-view structure of the SQL pipeline.
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")
CSV_NAME = "raw_fragrance_dataset_full.csv"  # <-- change to your actual filename
KAGGLE_DATASET = "owner/dataset-name"  # <-- fill in later if you wire up Kaggle

# Mirrors the column definitions in 01_create_raw_table.sql.
# Acts as the enforced schema for the raw load: every declared column
# must be present in the CSV, and each is loaded with the dtype below.
# <-- verify these against your CSV's header row
RAW_COLUMNS = {
    "url": "string",
    "Name": "string",
    "Gender": "string",
    "Rating Value": "string",   # converted to float in the clean stage
    "Rating Count": "string",   # converted to int in the clean stage
    "Main Accords": "string",   # list-like text, parsed in the clean stage
    "Perfumers": "string",      # list-like text, parsed in the clean stage
    "Description": "string",
}


def download_data() -> Path:
    """Fetch the raw dataset from Kaggle if it isn't already on disk."""
    csv_path = DATA_DIR / CSV_NAME
    if csv_path.exists():
        print(f"Found existing raw file: {csv_path}")
        return csv_path

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    import kaggle  # requires ~/.kaggle/kaggle.json
    kaggle.api.dataset_download_files(
        KAGGLE_DATASET, path=DATA_DIR, unzip=True
    )
    print(f"Downloaded dataset to {DATA_DIR}")
    return csv_path


def validate_schema(df: pd.DataFrame) -> None:
    """
    Check the loaded DataFrame against the declared RAW_COLUMNS schema.
    Equivalent to the implicit guarantee a SQL raw table gives you:
    the import fails loudly if the file doesn't match the table definition.
    """
    missing = set(RAW_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing expected columns: {sorted(missing)}. "
            f"Check RAW_COLUMNS against the file's header row."
        )

    extra = set(df.columns) - set(RAW_COLUMNS)
    if extra:
        print(f"Note: CSV contains undeclared columns (ignored downstream): {sorted(extra)}")


def load_raw(csv_path=None) -> pd.DataFrame:
    """Load the raw CSV. Equivalent to the raw table import in SQL."""
    if csv_path is None:
        csv_path = download_data()

    df = pd.read_csv(
        csv_path,
        dtype=RAW_COLUMNS,         # per-column dtypes from the declared schema
        encoding="utf-8",
        encoding_errors="replace", # handle odd characters in fragrance names
        on_bad_lines="warn",       # log malformed rows instead of crashing
    )
    validate_schema(df)
    print(f"Loaded {len(df):,} raw rows, {df.shape[1]} columns")
    return df


if __name__ == "__main__":
    df = load_raw()
    print(df.head())
    print(df.dtypes)