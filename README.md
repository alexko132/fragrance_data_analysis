# Fragrance Dataset Analysis

**End-to-End Data Pipeline: Python (pandas) + SQL + Tableau**

A dual-implementation ETL and analysis pipeline over ~70K web-scraped Fragrantica
records. The same cleaning logic is implemented twice — once in MySQL, once in
pandas — and both produce an identical 69,948-row validated dataset.

**[View the Tableau dashboard →](https://alexko132.github.io/fragrance_data_analysis/)** <!-- CHECK link -->

---

## 1. Project Overview

This project takes a raw, messy web-scraped fragrance dataset and turns it into a
validated analytical dataset, then answers business questions about brand
performance, gender segmentation, and perfumer influence.

The pipeline is implemented in **both SQL and Python**. This is intentional: the
two implementations are verified against each other, and agreement between them
is the project's core correctness guarantee. The Python implementation extends
the SQL version with automated testing and statistical analysis.

**Pipeline:** raw CSV → deduplication → cleaning & type coercion → automated
validation → cleaned dataset → Tableau dashboard + Jupyter analysis

---

## 2. Results at a Glance

| Metric | Value |
|---|---|
| Raw records ingested | 70,103 |
| Duplicate records removed | 155 |
| Cleaned records | **69,948** |
| Aggregate user ratings represented | 14,400,241 |
| Average rating | 3.98 / 5 |
| Automated quality checks passing | 8 / 8 |
| Gender split | Unisex 29,607 · Women 28,069 · Men 12,269 |

Both the SQL view and the pandas pipeline produce these figures independently.

---

## 3. Repository Structure

```
├── src/
│   ├── load_data.py        # Stage 1: acquisition + raw load (replaces 01, 02)
│   ├── clean_data.py       # Stage 2: dedup + cleaning (replaces 03)
│   └── pipeline.py         # Orchestration: load → clean → export
├── tests/
│   └── test_data_quality.py # Stage 3: 8 pytest checks (replaces 04)
├── notebooks/
│   └── analysis.ipynb      # Exploratory analysis + hypothesis testing
├── assets/
│   ├── sql/                # Original MySQL implementation (01–04)
│   ├── datasets/           # Sample CSV (full dataset excluded by size)
│   └── images/             # Dashboard screenshots
├── requirements.txt
└── README.md
```

### SQL → Python equivalence map

| SQL file | Python equivalent |
|---|---|
| `01_create_raw_table.sql` | `RAW_COLUMNS` schema spec in `load_data.py` |
| `02_import_data.sql` | `load_raw()` in `load_data.py` |
| `03_create_cleaned_view.sql` | `deduplicate()` + `clean()` in `clean_data.py` |
| `04_quality_checks.sql` | `tests/test_data_quality.py` (pytest) |

---

## 4. How to Run

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline (load → clean → export)
python3 src/pipeline.py

# Run the automated quality checks
python3 -m pytest tests/ -v
```

The full raw dataset exceeds GitHub's file size limit and is excluded via
`.gitignore`. A 1,000-row sample is included in `assets/datasets/` so the
pipeline structure can be inspected without the full file.

---

## 5. Cleaning Logic

Transformations applied identically in both implementations:

- **Deduplication** — records grouped by normalized URL (`TRIM(LOWER(url))` /
  `.str.strip().str.lower()`), keeping one row per fragrance.
- **Perfume name** — derived from the URL slug (strip `.html`, strip trailing
  numeric ID, replace hyphens with spaces), falling back to the raw `Name` field
  only when the URL yields nothing. The raw `Name` field is contaminated with
  brand and gender text (e.g. `"Sweet Coffee Anthologyfor women"`), so the URL is
  the more reliable source.
- **Brand** — extracted from the URL segment following `/perfume/`.
- **Gender** — standardized to Men / Women / Unisex via an **ordered** matching
  cascade. Order is load-bearing: `"women"` contains the substring `"men"`, so
  `women and men` → `unisex` → `women` → `men` must be evaluated in that
  sequence or every women's fragrance is misclassified.
- **Rating Value** — European decimal repair (`,` → `.`), regex validation
  against `^[0-9]+(\.[0-9]+)?$`, then cast to decimal. Non-conforming values
  become NULL rather than raising.
- **Rating Count** — all non-digit characters stripped (handles thousands
  separators), then cast to integer.
- **Main Accords** — list-like strings (`"['citrus', 'woody']"`) stripped of
  brackets and quotes, split on commas into five separate accord columns.

Raw columns are retained alongside cleaned ones (`Raw Name`, `Raw Gender`,
`Raw Main Accords`), which is what allows the quality checks to verify that no
value present in the raw data was lost during cleaning.

---

## 6. Data Quality Checks

All 8 checks pass on the current dataset. In Python they run as pytest
assertions, so validation is reproducible with one command rather than
manually re-run queries.

1. Total row count equals 69,948
2. No duplicate URLs
3. No perfume names lost during cleaning (present in raw, missing in cleaned)
4. No brands lost during cleaning
5. No accords lost during cleaning
6. `Gender` contains only Men / Women / Unisex / NULL
7. `Rating Value` falls within 0–5
8. `Rating Count` is never negative

---

## 7. Analysis & Key Findings

Full analysis in [`notebooks/analysis.ipynb`](notebooks/analysis.ipynb).

**Rating volume is extremely long-tailed.** The median fragrance has 26 ratings;
the mean is ~226, pulled up by a small number of blockbusters (max 29,858). This
finding drives the rest of the analysis: unweighted brand averages are unreliable,
so brand comparisons use a **volume-weighted mean** and a minimum catalog
threshold.

**Ratings themselves are tightly clustered.** Median 4.0, mean 3.98, standard
deviation 0.52, IQR 3.75–4.25 — left-skewed, with a longer tail toward low
ratings than high. Meaningful differences between segments are therefore small
in absolute terms.

**Catalog size does not predict quality.** Across 1,534 brands with at least 10
fragrances, the correlation between catalog size and volume-weighted rating is
r ≈ -0.07 — effectively nil. Prolific houses are neither systematically better
nor worse than selective ones. However, the choice of averaging method matters a
great deal for individual brands: the simple mean overstates quality by as much
as 0.33 points (Dzintars) and 0.19 points (The Dua Brand), while understating it
by 0.14 points (Al Haramain Perfumes).

**Gender differences are statistically significant but practically negligible.**
One-way ANOVA (p = 5.7e-32) and Kruskal-Wallis (p = 5.1e-92) both reject the null
hypothesis — but at n = 69,948, nearly any difference will. Effect size tells the
real story: eta-squared = 0.0023, meaning gender explains roughly **0.2%** of
rating variance. The largest gap (Women vs. Unisex, 0.055 rating points) has
Cohen's d = -0.10, below the conventional threshold for a "small" effect. The
practical conclusion is that gender segmentation is not a useful predictor of
fragrance rating.

**Perfumer data is directional only.** 61.1% of records have no perfumer
credited, so perfumer-level results should not be read as population-level
claims. Among the 406 perfumers with at least 20 credited fragrances, the
highest volume-weighted averages cluster between 4.43 and 4.69.

---

## 8. Known Data Limitations

- **Perfumer coverage** — 61.1% of records have no perfumer credited.
- **Perfumer name fragmentation** — near-duplicate name spellings appear in the
  source data (e.g. `"Fahran S Ali"` / `"Mahran S Ali"` share identical
  fragrance counts and ratings, indicating a scrape artifact rather than two
  individuals). <!-- CHECK: update with the fuzzy-match pair count once run -->
  Perfumer-level counts are therefore lower bounds. Names were left unmodified
  rather than manually merged, since no authoritative source resolves the
  correct spelling.
- **Unclassifiable gender** — 3 records have gender text that matches none of
  the mapping patterns and are retained as NULL.
- **Scope difference between implementations** — the Python pipeline retains the
  `Perfumers` column, which the SQL view does not carry. All shared columns,
  the row count, and every KPI are identical between the two implementations.
- **Rating recency** — the dataset is a point-in-time scrape; ratings and counts
  reflect the date of collection, not current values.

---

## 9. Tools

**Python** (pandas, matplotlib, seaborn, scipy, pytest, Jupyter) ·
**MySQL** · **Tableau** · **Git / GitHub Pages**
