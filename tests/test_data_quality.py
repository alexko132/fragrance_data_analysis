"""
Stage 3: Data quality tests.
Replaces 04_quality_checks.sql — each SQL check becomes a pytest test.
Run with: python3 -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from clean_data import build_cleaned


@pytest.fixture(scope="session")
def df():
    """Build the cleaned dataset once, share it across all tests."""
    return build_cleaned()


def test_row_count(df):
    """Check 1: total rows match the published figure."""
    assert len(df) == 69_948


def test_no_duplicate_urls(df):
    """Check 2: no URL appears more than once."""
    assert df["URL"].duplicated().sum() == 0


def test_no_names_lost_in_cleaning(df):
    """Check 3a: raw Name present but cleaned Perfume missing -> 0 rows."""
    raw_has_name = df["Raw Name"].notna() & (df["Raw Name"].str.strip() != "")
    cleaned_missing = df["Perfume"].isna() | (df["Perfume"].str.strip() == "")
    assert (raw_has_name & cleaned_missing).sum() == 0


def test_no_brands_lost_in_cleaning(df):
    """Check 3b: URL contains /perfume/ segment but Brand missing -> 0 rows."""
    has_perfume_url = df["URL"].str.contains("/perfume/", na=False)
    cleaned_missing = df["Brand"].isna() | (df["Brand"].str.strip() == "")
    assert (has_perfume_url & cleaned_missing).sum() == 0


def test_no_accords_lost_in_cleaning(df):
    """Check 3c: raw accords present but all 5 cleaned accords missing -> 0 rows."""
    raw_has_accords = df["Raw Main Accords"].notna()
    accord_cols = [f"Main Accord {i}" for i in range(1, 6)]
    all_missing = df[accord_cols].isna().all(axis=1)
    assert (raw_has_accords & all_missing).sum() == 0


def test_gender_values_valid(df):
    """Check 4a: Gender is only Men, Women, Unisex, or null."""
    invalid = df["Gender"].dropna()[~df["Gender"].dropna().isin(["Men", "Women", "Unisex"])]
    assert len(invalid) == 0


def test_rating_values_in_range(df):
    """Check 4b: Rating Value between 0 and 5."""
    rv = df["Rating Value"].dropna()
    assert ((rv < 0) | (rv > 5)).sum() == 0


def test_rating_counts_not_negative(df):
    """Check 4c: Rating Count is never negative."""
    assert (df["Rating Count"].dropna() < 0).sum() == 0
    