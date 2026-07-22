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
Turning unreliable scraped fragrance data into a trusted asset for brand strategy decisions

---

## 1. Project Overview

A fragrance brand, retailer, or new market entrant making decisions about portfolio strategy — which scent categories to invest in, which brands to benchmark against, which accords to prioritize in R&D — needs reliable data to base those decisions on. The only data available in this space is typically scraped from review platforms: unstructured, duplicated, and inconsistently formatted, making it unsafe to use for any real business decision without significant cleanup.

This project was scoped and executed as a consulting-style engagement: **turn an unreliable raw dataset into a trusted analytical asset, then use it to recommend where a fragrance brand should focus.** MySQL was used to clean, deduplicate, and validate 69,948 fragrance records, and Tableau was used to surface the trends a product or brand strategy team would actually act on.

The guiding question behind every technical decision in this project was not "how do I clean this data" but **"what would a brand's leadership team need to trust before making a portfolio decision off of it?"**

![Fragrance Dataset Overview Dashboard](assets/images/tableau_final_dashboard.png)

- **Dataset source:** Sample included in `assets/datasets/`; full raw dataset excluded due to GitHub file size limits
- **Tableau Public:** Not published yet
- **GitHub repository:** Current repository

---

## Project Links

- [User Requirements Document PDF](assets/docs/user_requirements_document.pdf)
- [User Requirements Document DOCX](assets/docs/user_requirements_document.docx)
- [Sample Raw Dataset](assets/datasets/raw_fragrance_dataset_sample.csv)
- [Dataset Note](assets/datasets/dataset_note.md)
- [SQL Files](assets/sql/)
- [Project Screenshots](assets/images/)

---

## 2. Business/Data Questions

Framed as the questions a brand strategy or product team would bring to an analyst:

- **Where is the market crowded, and where is there white space?** (fragrance distribution across Men, Women, Unisex)
- **Who are we actually competing against, and at what scale?** (brand-level share of the dataset)
- **What actually earns high ratings once we filter out noise?** (top-rated fragrances at 100+ ratings, to avoid chasing false signals from low-volume outliers)
- **What scent profiles dominate consumer preference, and where might there be differentiation opportunity?** (most common primary accords)
- **Can we trust this data enough to act on it?** (this had to be answered first — before any of the above questions were worth asking)

---

## 3. Tools Used

- **MySQL** – data cleaning, deduplication, transformation, and validation
- **Tableau** – dashboard creation and visualization
- **GitHub** – project documentation and version control
- **CSV / raw dataset** – original data source

---

## 4. Dataset Description

The raw dataset contained fragrance records with the following fields:

- URL
- Name
- Gender
- Rating Value
- Rating Count
- Main Accords
- Perfumers
- Description

Before any of the questions in Section 2 could be answered responsibly, the raw data had to be brought up to a standard a stakeholder could trust. As received, it had several problems that would have made any downstream recommendation unreliable:

- Perfume names had to be extracted from URLs
- Brand names had to be extracted from URLs
- Gender values needed to be standardized
- Rating values needed to be converted into numeric decimal values
- Rating counts needed to be converted into numeric whole numbers
- Main accords were stored as list-like text (e.g., `['citrus', 'musky', 'woody', ...]`) and needed to be cleaned and split into separate columns
- Duplicate records needed to be removed using normalized URLs

Shipping a dashboard on top of this data without addressing these issues first would have meant handing a client a set of numbers that looked authoritative but weren't — duplicated records inflating brand counts, malformed ratings skewing averages, and unstandardized gender values fragmenting what should have been a single category.

> Note: The full raw dataset is not included in this repository because it exceeds GitHub's file size limit. A smaller sample file, `raw_fragrance_dataset_sample.csv`, is included in `assets/datasets/` for preview purposes. The SQL cleaning process was performed locally on the full dataset, and the final cleaned view contained 69,948 fragrance records.

---

## 5. Data Cleaning Process

All cleaning was performed in MySQL. The full SQL is available in the `assets/sql/` folder; the process is summarized below.

**Main SQL objects:**

- `fra_perfumes_raw` – raw imported table
- `fra_perfumes_raw_deduped` – deduplicated table
- `vw_fragrances_cleaned` – cleaned SQL view used for analysis and the dashboard

**Deduplication (`fra_perfumes_raw_deduped`):**

1. Grouped records by `TRIM(LOWER(url))` so that each duplicate group represented the same fragrance record under a normalized URL.
2. Used `MIN(url)` to keep one URL per duplicate group.
3. Used `MAX()` on Name, Gender, Rating Value, Rating Count, and Main Accords to select one representative non-null value from each duplicate group when available.

**Cleaning and transformation (`vw_fragrances_cleaned`):**

4. Extracted perfume names from the last section of the URL, using the raw Name field as a fallback when the URL-derived name was missing or blank.
5. Extracted brand names from the URL section after `/perfume/`.
6. Standardized gender into three values: Men, Women, and Unisex.
7. Converted rating values into decimal numbers.
8. Converted rating counts into unsigned integers.
9. Cleaned the Main Accords field by removing brackets and apostrophes.
10. Split the cleaned accords into separate columns: Main Accord 1 through Main Accord 5.

See `assets/sql/03_create_cleaned_view.sql` for the full transformation logic.

---

## 6. Data Quality Checks

Before building the dashboard — and before any finding in Section 9 could be presented to a stakeholder as trustworthy — a set of SQL validation checks was run against the cleaned view (see `assets/sql/04_quality_checks.sql`). This is the step I'd insist on before letting any number reach a client deck: a clean-looking dashboard built on unverified data is worse than no dashboard at all, because it invites confident decisions on bad information. Each check is documented with a screenshot in the `assets/images/` folder.

The pipeline is implemented in **both SQL and Python**. This is intentional: the
two implementations are verified against each other, and agreement between them
is the project's core correctness guarantee. The Python implementation extends
the SQL version with automated testing and statistical analysis.

**Pipeline:** raw CSV → deduplication → cleaning & type coercion → automated
validation → cleaned dataset → Tableau dashboard + Jupyter analysis
All checks passed, confirming the cleaned dataset was ready to support the recommendations in Section 9.

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

Each visualization was chosen to answer one of the business questions in Section 2 directly — the goal was a dashboard a stakeholder could read in under a minute and walk away from with a clear next question, not a wall of exploratory charts.

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
## 9. Insights & Recommendations

Each finding below is presented the way I'd bring it to a product or brand strategy team: the data point, what it implies, and the decision or follow-up question it should drive.

### Finding 1: Category crowding — Unisex and Women's fragrances dominate
Unisex fragrances are the largest segment (29,607 records), Women's is close behind (28,069), and Men's is a distant third (12,269).

**Recommendation:** A brand entering the Men's category faces less direct competition by volume — but before treating this as white space, I'd flag it as a question rather than a conclusion: is Men's genuinely a smaller market, or is it under-tagged/mislabeled in the source data? I'd recommend validating this against a second data source (e.g., retail sales data) before committing R&D budget on the assumption that Men's is underserved.

### Finding 2: Brand concentration — a handful of brands dominate volume
The Dua Brand (1,638), Avon (1,284), and Zara (946) lead the dataset by fragrance count, well ahead of prestige names like Guerlain (526).

**Recommendation:** High record count reflects catalog breadth, not necessarily market share or quality — a brand shouldn't benchmark against The Dua Brand or Avon assuming they're the biggest competitive threat just because they have the most SKUs. I'd recommend pairing this chart with a rating-weighted or revenue-weighted view before using it to prioritize competitive response.

### Finding 3: Accord saturation — Woody and Citrus dominate consumer-facing scent profiles
Woody (9,718) and Citrus (9,280) are the two most common primary accords by a wide margin over categories like Vanilla (2,476) or Warm Spicy (3,635).

**Recommendation:** A brand launching a new fragrance in Woody or Citrus is entering the most saturated part of the market and will need a clear differentiation angle (packaging, price point, brand story) to stand out. Conversely, less common accords like Vanilla or Warm Spicy represent lower competitive density — worth a follow-up analysis on whether that's due to lower consumer demand or simply less industry investment, since those have very different strategic implications.

### Finding 4: Rating quality — high scores mean nothing without volume
The top-rated fragrances (e.g., Spiderman at 4.83, The Heritage Blend at 4.79) only became a reliable signal once filtered to fragrances with 100+ ratings; without that filter, the leaderboard would have been dominated by low-volume outliers with a handful of 5-star reviews.

**Recommendation:** This is the kind of filtering decision I'd insist on before letting any "top rated" list reach a stakeholder deck — an unfiltered ranking would have led a team to chase products that aren't actually validated by the market. Any future rating-based analysis (e.g., brand quality scoring) should carry the same minimum-volume threshold forward.

> **Caveat for all four findings:** this dataset reflects what a scraping pipeline pulled from public review pages, not verified retail sales or a market research panel. I'd present these findings to a client as directional and hypothesis-generating — a strong starting point for where to dig deeper, not a final verdict.

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
This project was structured the way a consulting or product analytics engagement would be: start from a business problem (an unreliable dataset that can't safely inform decisions), build the technical foundation to solve it, and end with recommendations a leadership team could act on. That included:

- Identifying why the raw data was unsafe to use for decision-making in its original form
- SQL data cleaning, deduplication, and transformation to build a trustworthy dataset
- Repeatable data validation checks, treated as a gate before any finding could be presented as reliable
- Dashboard design and KPI selection aimed at the specific questions a stakeholder would ask
- Translating each data finding into a recommendation or a flagged follow-up question, rather than stopping at description
- Being explicit about the limits of the data (scraped review data vs. verified sales/market data) so recommendations aren't overstated

These are the same steps required in a real business setting when raw operational or scraped data needs to be converted into a reliable reporting layer that a team can actually make decisions from.

---

## 9. Tools

**Python** (pandas, matplotlib, seaborn, scipy, pytest, Jupyter) ·
**MySQL** · **Tableau** · **Git / GitHub Pages**
- Add additional accord columns (beyond Main Accord 1–5) or model accords in a normalized long format for deeper analysis.
- Analyze the relationship between rating value, rating count, and gender category.
- Add brand-level average ratings to compare brand quality, not just volume — directly addressing the caveat in Finding 2.
- Validate the Men's fragrance gap (Finding 1) against an external retail or sales dataset.
- Automate the cleaning pipeline with stored procedures or a scheduled ETL job.
- Publish the dashboard to Tableau Public and add interactive filters (brand, gender, accord).
