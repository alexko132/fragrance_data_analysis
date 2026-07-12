"""
Stage 2: Deduplication and cleaning.
Faithful pandas translation of fra_perfumes_raw_deduped +
03_create_cleaned_view.sql (vw_fragrances_cleaned).
"""

import pandas as pd
from load_data import load_raw


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Replicates fra_perfumes_raw_deduped:
    group by TRIM(LOWER(url)), MIN(url), MAX() of other fields."""
    df = df.copy()
    df["url_key"] = df["url"].str.strip().str.lower()
    deduped = df.groupby("url_key", as_index=False).agg(
        url=("url", "min"),
        Name=("Name", "max"),
        Gender=("Gender", "max"),
        **{
            "Rating Value": ("Rating Value", "max"),
            "Rating Count": ("Rating Count", "max"),
            "Main Accords": ("Main Accords", "max"),
            "Perfumers": ("Perfumers", "max"),
            "Description": ("Description", "max"),
        },
    ).drop(columns="url_key")
    print(f"Deduplicated: {len(df):,} -> {len(deduped):,} rows "
          f"({len(df) - len(deduped):,} duplicates removed)")
    return deduped


def standardize_gender(raw: pd.Series) -> pd.Series:
    """Replicates the ordered CASE/LIKE cascade — order matters, because
    'women' contains 'men', so Unisex and Women must match first."""
    g = raw.str.strip().str.lower().fillna("")
    out = pd.Series(pd.NA, index=raw.index, dtype="string")
    out = out.mask(g.str.contains("women and men", regex=False), "Unisex")
    out = out.mask(out.isna() & g.str.contains("men and women", regex=False), "Unisex")
    out = out.mask(out.isna() & g.str.contains("unisex", regex=False), "Unisex")
    out = out.mask(out.isna() & g.str.contains("women", regex=False), "Women")
    out = out.mask(out.isna() & g.str.contains("female", regex=False), "Women")
    out = out.mask(out.isna() & g.str.contains("men", regex=False), "Men")
    out = out.mask(out.isna() & g.str.contains("male", regex=False), "Men")
    return out


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Replicates vw_fragrances_cleaned, keeping raw columns like the view does."""
    out = pd.DataFrame(index=df.index)
    out["URL"] = df["url"]
    out["Raw Name"] = df["Name"]

    # -- Perfume: derived from URL, fallback to trimmed raw Name --
    clean_from_url = (
        df["url"].str.strip()
        .str.rsplit("/", n=1).str[-1]
        .str.replace(r"\.html$", "", regex=True)
        .str.replace(r"-[0-9]+$", "", regex=True)
        .str.replace("-", " ", regex=False)
        .str.strip()
    )
    name_fallback = df["Name"].str.strip().replace("", pd.NA)
    out["Perfume"] = clean_from_url.where(
        clean_from_url.notna() & (clean_from_url != ""), name_fallback
    )

    # -- Brand: segment after /perfume/, dashes -> spaces --
    out["Brand"] = (
        df["url"].str.strip()
        .str.split("/perfume/").str[-1]
        .str.split("/").str[0]
        .str.replace("-", " ", regex=False)
        .str.strip()
    )

    out["Raw Gender"] = df["Gender"]
    out["Gender"] = standardize_gender(df["Gender"])

    # -- Rating Value: N/A -> null, comma -> dot, validate numeric pattern --
    out["Raw Rating Value"] = df["Rating Value"]
    rv = df["Rating Value"].str.strip()
    rv = rv.mask(rv.str.upper() == "N/A").replace("", pd.NA)
    rv = rv.str.replace(",", ".", regex=False)
    rv = rv.where(rv.str.fullmatch(r"[0-9]+(\.[0-9]+)?", na=False))
    out["Rating Value"] = pd.to_numeric(rv, errors="coerce")

    # -- Rating Count: N/A -> null, strip non-digits, validate --
    out["Raw Rating Count"] = df["Rating Count"]
    rc = df["Rating Count"].str.strip()
    rc = rc.mask(rc.str.upper() == "N/A")
    rc = rc.str.replace(r"[^0-9]", "", regex=True).replace("", pd.NA)
    out["Rating Count"] = pd.to_numeric(rc, errors="coerce").astype("Int64")

    # -- Main Accords: null out empties/'[]', strip brackets+quotes, split to 5 --
    ma = df["Main Accords"].str.strip()
    ma = ma.mask((ma == "") | (ma == "[]"))
    out["Raw Main Accords"] = ma
    clean_accords = (
        ma.str.replace("[", "", regex=False)
          .str.replace("]", "", regex=False)
          .str.replace("'", "", regex=False)
    )
    split = clean_accords.str.split(",")
    for i in range(5):
        col = split.str[i].str.strip().replace("", pd.NA)
        out[f"Main Accord {i+1}"] = col

    return out


def build_cleaned(df_raw=None) -> pd.DataFrame:
    if df_raw is None:
        df_raw = load_raw()
    return clean(deduplicate(df_raw))


if __name__ == "__main__":
    df = build_cleaned()
    print("\n--- Verification against SQL results ---")
    print(f"Rows:          {len(df):,}   (target: 69,948)")
    print(f"Avg rating:    {df['Rating Value'].mean():.2f}   (target: 3.98)")
    print(f"Total ratings: {df['Rating Count'].sum():,}   (target: 14,400,241)")
    print(f"\nGender counts (targets: Unisex 29,607 / Women 28,069 / Men 12,269):")
    print(df["Gender"].value_counts(dropna=False))
    