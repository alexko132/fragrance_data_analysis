# Fragrance Dataset Analysis

**End-to-End Data Pipeline: Python (pandas) + SQL + Tableau**

Turning unreliable scraped fragrance data into a trusted asset for brand strategy decisions — implemented twice, once in MySQL and once in pandas, with both pipelines verified to produce an identical validated dataset.

**Dashboard:** Not yet published to Tableau Public. Screenshots documenting the dashboard and full pipeline are available in `assets/images/`.

---

## 1. Project Overview

A fragrance brand, retailer, or new market entrant making decisions about portfolio strategy — which scent categories to invest in, which brands to benchmark against, which accords to prioritize in R&D — needs reliable data to base those decisions on. The only data available in this space is typically scraped from review platforms: unstructured, duplicated, and inconsistently formatted, making it unsafe to use for any real business decision without significant cleanup.

This project was scoped and executed as a consulting-style engagement: **turn an unreliable raw dataset into a trusted analytical asset, then use it to recommend where a fragrance brand should focus.** The cleaning and validation logic was implemented twice — once in MySQL, once in Python/pandas — as a correctness check: if both independent implementations produce the same 69,948-row dataset and the same KPIs, that agreement is stronger evidence the numbers can be trusted than either implementation alone.

The guiding question behind every technical decision in this project was not "how do I clean this data" but **"what would a brand's leadership team need to trust before making a portfolio decision off of it?"**

- **Dataset source:** Sample included in `assets/datasets/`; full raw dataset excluded due to GitHub file size limits
- **Tableau Public:** Not published — see `assets/images/tableau_final_dashboard.png` for the finished dashboard
- **GitHub repository:** Current repository

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

- **MySQL** – original cleaning, deduplication, transformation, and validation implementation
- **Python (pandas, pytest)** – second independent implementation of the same pipeline, plus statistical analysis (scipy) and exploratory work (Jupyter, matplotlib, seaborn)
- **Tableau** – dashboard creation and visualization
- **Git / GitHub / GitHub Pages** – version control and project documentation

---

## 4. Dataset Description

The raw dataset contained fragrance records with the following fields: URL, Name, Gender, Rating Value, Rating Count, Main Accords, Perfumers, Description.

Before any of the questions in Section 2 could be answered responsibly, the raw data had to be brought up to a standard a stakeholder could trust. As received, it had several problems that would have made any downstream recommendation unreliable:

- Perfume names had to be extracted from URLs (the raw `Name` field is contaminated with brand and gender text, e.g. `"Sweet Coffee Anthologyfor women"`, making the URL the more reliable source)
- Brand names had to be extracted from URLs
- Gender values needed to be standardized
- Rating values needed to be converted into numeric decimal values (including repairing European-style decimals, e.g. `4,5` → `4.5`)
- Rating counts needed to be converted into numeric whole numbers (stripping thousands separators)
- Main accords were stored as list-like text (e.g., `['citrus', 'musky', 'woody', ...]`) and needed to be cleaned and split into separate columns
- Duplicate records needed to be removed using normalized URLs

Shipping a dashboard on top of this data without addressing these issues first would have meant handing a client a set of numbers that looked authoritative but weren't — duplicated records inflating brand counts, malformed ratings skewing averages, and unstandardized gender values fragmenting what should have been a single category.

> Note: The full raw dataset is not included in this repository because it exceeds GitHub's file size limit. A smaller sample file is included in `assets/datasets/` for preview purposes. Both implementations were run against the full dataset locally, producing a final cleaned dataset of 69,948 fragrance records.

---

## 5. Repository Structure

```
fragrance_data_analysis/
├── README.md
├── requirements.txt
├── _config.yml
│
├── src/
│   ├── load_data.py         # Stage 1: acquisition + raw load
│   ├── clean_data.py        # Stage 2: dedup + cleaning
│   └── pipeline.py          # Orchestration: load → clean → export
│
├── tests/
│   └── test_data_quality.py # 8 automated pytest quality checks
│
├── notebooks/
│   └── analysis.ipynb       # Exploratory analysis + hypothesis testing
│
├── data/
│   └── processed/
│       └── fragrances_cleaned.csv
│
└── assets/
    ├── sql/                 # Original MySQL implementation (01–04)
    ├── datasets/            # Sample raw CSV (full dataset excluded by size)
    ├── docs/                # User requirements document
    └── images/              # Dashboard + pipeline screenshots
```

### SQL → Python equivalence map

| SQL file | Python equivalent |
|---|---|
| `01_create_raw_table.sql` | Schema definition in `load_data.py` |
| `02_import_data.sql` | `load_raw()` in `load_data.py` |
| `03_create_cleaned_view.sql` | `deduplicate()` + `clean()` in `clean_data.py` |
| `04_quality_checks.sql` | `tests/test_data_quality.py` (pytest) |

---

## 6. Data Cleaning Process

The same transformation logic is implemented in both `assets/sql/03_create_cleaned_view.sql` and `src/clean_data.py`.

**Deduplication:** Records grouped by normalized URL (`TRIM(LOWER(url))` in SQL / `.str.strip().str.lower()` in pandas), keeping one representative row per fragrance.

**Perfume name:** Derived from the URL slug (strip `.html`, strip trailing numeric ID, replace hyphens with spaces), falling back to the raw `Name` field only when the URL yields nothing.

**Brand:** Extracted from the URL segment following `/perfume/`.

**Gender:** Standardized to Men / Women / Unisex via an **ordered** matching cascade. The order is load-bearing — `"women"` contains the substring `"men"`, so the check for `"women and men"` → `"unisex"` must run before the checks for `"women"` and `"men"` individually, or every women's fragrance gets misclassified. This is the kind of bug that would have silently corrupted the gender KPI if the SQL and Python versions hadn't been cross-checked against each other.

**Rating Value:** Decimal repair (`,` → `.`), regex validation, then cast to decimal. Non-conforming values become NULL rather than raising an error.

**Rating Count:** All non-digit characters stripped, then cast to integer.

**Main Accords:** List-like strings stripped of brackets and quotes, then split into five separate accord columns.

Raw columns are retained alongside cleaned ones in the Python implementation (`Raw Name`, `Raw Gender`, `Raw Main Accords`), which is what allows the quality checks to verify that no value present in the raw data was silently lost during cleaning.

---

## 7. Data Quality Checks

Before any finding in Section 13 could be presented as trustworthy, a set of validation checks was run against the cleaned data — as SQL queries against the view, and as pytest assertions against the pandas output. This is the step I'd insist on before letting any number reach a client deck: a clean-looking dashboard built on unverified data is worse than no dashboard at all, because it invites confident decisions on bad information.

| Check | Rule | Result |
|---|---|---|
| Row count check | Confirms the total row count of the cleaned dataset | 69,948 rows |
| Duplicate URL check | Should return 0 rows after deduplication | Passed (0 duplicates) |
| Missing cleaned perfume name check | Cleaned names should not become missing if raw data had usable values | Passed (0 rows) |
| Missing cleaned brand check | Cleaned brands should not become missing if raw data had usable values | Passed (0 rows) |
| Missing cleaned accords check | Cleaned accords should not become missing if raw data had usable values | Passed (0 rows) |
| Invalid gender value check | Gender must only be Men, Women, Unisex, or NULL | Passed (0 invalid values) |
| Invalid rating value check | Rating Value must be between 0 and 5 | Passed (0 invalid values) |
| Invalid rating count check | Rating Count cannot be negative | Passed (0 invalid values) |

All 8 checks pass in both implementations. In Python, they run as pytest assertions, so validation is reproducible with a single command rather than manually re-running queries.

---

## 8. How to Run

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

The full raw dataset exceeds GitHub's file size limit and is excluded via `.gitignore`. A sample is included in `assets/datasets/` so the pipeline structure can be inspected without the full file — reproducing the exact final numbers requires the full raw dataset.

For the SQL implementation: run the files in `assets/sql/` in order (create raw table → import data → create cleaned view → quality checks), then connect Tableau to the resulting view.

---

## 9. Results at a Glance

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

## 10. Dashboard Overview

**Title:** Fragrance Dataset Overview

**KPIs:** Total Fragrances (69,948) · Average Rating (3.98) · Total Rating Count (14,400,241)

**Visualizations:** Fragrances by Gender (bar chart) · Top Brands by Fragrance Count (bar chart) · Top Rated Fragrances with 100+ Ratings (bar chart) · Most Common Primary Accords (treemap)

Each visualization was chosen to answer one of the business questions in Section 2 directly — the goal was a dashboard a stakeholder could read in under a minute and walk away from with a clear next question, not a wall of exploratory charts.

---

## 11. Key Results

**Fragrances by Gender**

| Gender | Fragrance Count |
|---|---|
| Unisex | 29,607 |
| Women | 28,069 |
| Men | 12,269 |

> Note: totals 69,945; the remaining 3 records had unclassifiable gender text and are retained as NULL.

**Top Brands by Fragrance Count**

| Brand | Fragrance Count |
|---|---|
| The Dua Brand | 1,638 |
| Avon | 1,284 |
| Zara | 946 |
| Victoria's Secret | 764 |
| Bath & Body Works | 623 |
| Jequiti | 621 |
| O Boticario | 551 |
| Guerlain | 526 |
| Natura | 466 |
| Dzintars | 464 |

**Top Rated Fragrances with 100+ Ratings**

| Fragrance | Avg. Rating |
|---|---|
| Spiderman | 4.83 |
| The Heritage Blend | 4.79 |
| Taif Rose | 4.79 |
| Palace Oud | 4.79 |
| Alhambra Oud | 4.72 |
| Hard Candy Elixir | 4.71 |
| Vol de Nuit Extract | 4.70 |
| Roberto Cavalli Uomo Gold | 4.69 |
| Estee Extrait | 4.69 |
| Aoud Absolue Precieux | 4.69 |

**Most Common Primary Accords**

| Accord | Count |
|---|---|
| Woody | 9,718 |
| Citrus | 9,280 |
| Fruity | 5,530 |
| White Floral | 5,181 |
| Floral | 4,910 |
| Aromatic | 4,229 |
| Amber | 4,112 |
| Warm Spicy | 3,635 |
| Sweet | 3,327 |
| Vanilla | 2,476 |

---

## 12. Deeper Statistical Analysis

Full analysis in [`notebooks/analysis.ipynb`](notebooks/analysis.ipynb). These findings go beyond the dashboard KPIs and directly inform the recommendations in Section 13.

**Rating volume is extremely long-tailed.** The median fragrance has 26 ratings; the mean is ~226, pulled up by a small number of blockbusters (max 29,858). This is *why* the top-rated ranking in Section 11 required a 100+ rating floor — an unweighted ranking would be dominated by low-volume outliers with a handful of 5-star reviews.

**Catalog size does not predict quality.** Across 1,534 brands with at least 10 fragrances, the correlation between catalog size and volume-weighted rating is r ≈ -0.07 — effectively no relationship. But the choice of averaging method matters a great deal for individual brands: a simple mean overstates quality by as much as 0.33 points (Dzintars) and 0.19 points (The Dua Brand) versus a volume-weighted mean, while understating it by 0.14 points for Al Haramain Perfumes.

**Gender differences are statistically significant but practically negligible.** One-way ANOVA (p = 5.7e-32) and Kruskal-Wallis (p = 5.1e-92) both reject the null hypothesis — but at n = 69,948, nearly any difference will clear that bar. Effect size tells the real story: eta-squared = 0.0023, meaning gender explains roughly 0.2% of rating variance, and the largest pairwise gap (Women vs. Unisex, 0.055 points) has a Cohen's d of -0.10 — below the conventional threshold for even a "small" effect.

**Perfumer data is directional only.** 61.1% of records have no perfumer credited, so perfumer-level results should not be read as population-level claims. Among the 406 perfumers with at least 20 credited fragrances, the highest volume-weighted averages cluster between 4.43 and 4.69.

---

## 13. Insights & Recommendations

Each finding below is presented the way I'd bring it to a product or brand strategy team: the data point, what it implies, and the decision or follow-up question it should drive.

### Finding 1: Category crowding by volume, but gender itself doesn't predict rating
Unisex fragrances are the largest segment by volume (29,607 records), Women's is close behind (28,069), and Men's is a distant third (12,269). However, the statistical analysis in Section 12 shows gender explains only ~0.2% of rating variance (eta-squared = 0.0023) — a negligible effect despite being statistically significant at this sample size.

**Recommendation:** A brand entering the Men's category faces less direct competition by volume, and the data confirms gender segment isn't itself driving quality differences — so this isn't a case of "the smaller category is smaller because it's worse." That said, before treating Men's as white space, I'd still flag it as a question: is it a genuinely smaller market, or under-tagged in the source data? I'd recommend validating against a second data source (e.g., retail sales data) before committing R&D budget.

### Finding 2: Brand concentration by volume, but volume ≠ quality
The Dua Brand (1,638), Avon (1,284), and Zara (946) lead by fragrance count, well ahead of prestige names like Guerlain (526). But across 1,534 brands, catalog size and volume-weighted rating are essentially uncorrelated (r ≈ -0.07), and unweighted averages can overstate a brand's real quality by up to 0.33 points.

**Recommendation:** A brand shouldn't benchmark against The Dua Brand or Avon assuming they're the biggest competitive threat just because they have the most SKUs, and any brand-quality comparison needs a volume-weighted mean with a minimum catalog threshold — a simple average is measurably misleading here, not just theoretically imprecise.

### Finding 3: Accord saturation — Woody and Citrus dominate consumer-facing scent profiles
Woody (9,718) and Citrus (9,280) are the two most common primary accords by a wide margin over categories like Vanilla (2,476) or Warm Spicy (3,635).

**Recommendation:** A brand launching a new fragrance in Woody or Citrus is entering the most saturated part of the market and will need a clear differentiation angle (packaging, price point, brand story) to stand out. Less common accords like Vanilla or Warm Spicy represent lower competitive density — worth a follow-up analysis on whether that reflects lower consumer demand or simply less industry investment, since those imply very different strategies.

### Finding 4: Rating quality — high scores mean nothing without volume
The top-rated fragrances (e.g., Spiderman at 4.83) only became a reliable signal once filtered to 100+ ratings — a direct consequence of the long-tailed rating distribution documented in Section 12.

**Recommendation:** This is the kind of filtering decision I'd insist on before letting any "top rated" list reach a stakeholder deck. Any future rating-based analysis should carry the same minimum-volume threshold forward.

### Finding 5: Perfumer influence is a promising but unverified signal
Among perfumers with 20+ credited fragrances, volume-weighted averages cluster between 4.43–4.69 — but 61.1% of records have no perfumer credited at all.

**Recommendation:** I would not present perfumer-level rankings to a client as a reliable signal yet — the coverage gap is too large. This is a "worth investing in better source data before acting on it" finding, not a "here's your answer" finding.

> **Caveat for all five findings:** this dataset reflects what a scraping pipeline pulled from public review pages, not verified retail sales or a market research panel. I'd present these findings to a client as directional and hypothesis-generating — a strong starting point for where to dig deeper, not a final verdict.

---

## 14. Known Data Limitations

- **Perfumer coverage** — 61.1% of records have no perfumer credited.
- **Perfumer name fragmentation** — near-duplicate name spellings appear in the source data (e.g. `"Fahran S Ali"` / `"Mahran S Ali"` share identical fragrance counts and ratings, indicating a scrape artifact rather than two individuals). Names were left unmodified rather than manually merged, since no authoritative source resolves the correct spelling.
- **Unclassifiable gender** — 3 records have gender text matching none of the mapping patterns and are retained as NULL.
- **Scope difference between implementations** — the Python pipeline retains the `Perfumers` column, which the SQL view does not carry. All shared columns, the row count, and every KPI are identical between the two implementations.
- **Rating recency** — the dataset is a point-in-time scrape; ratings and counts reflect the date of collection, not current values.

---

## 15. Project Evidence / Screenshots

The `assets/images/` folder documents each stage of the project so the work can be verified without re-running the pipeline: raw data previews, deduplicated table preview, cleaned view previews, and one screenshot per quality check.

---

## 16. Business/Portfolio Value

This project was structured the way a consulting or product analytics engagement would be: start from a business problem (an unreliable dataset that can't safely inform decisions), build the technical foundation to solve it — twice, independently, as a correctness check — and end with recommendations a leadership team could act on. That included:

- Identifying why the raw data was unsafe to use for decision-making in its original form
- Implementing the same cleaning and validation logic independently in SQL and Python, using agreement between the two as a correctness guarantee
- Automated, repeatable data validation (SQL queries and pytest), treated as a gate before any finding could be presented as reliable
- Statistical rigor beyond descriptive stats — hypothesis testing and effect sizes to distinguish "statistically significant" from "practically meaningful"
- Translating each data finding into a recommendation or a flagged follow-up question, rather than stopping at description
- Being explicit about the limits of the data so recommendations aren't overstated

---

## 17. Future Improvements

- Resolve the perfumer name-fragmentation issue with fuzzy matching, and report the confirmed collision count
- Add brand-level average ratings using the volume-weighted method as the default reporting standard, given the divergence documented in Section 12
- Validate the Men's fragrance gap (Finding 1) against an external retail or sales dataset
- Publish the dashboard to Tableau Public and add interactive filters (brand, gender, accord)
- Schedule the pipeline (SQL or Python) as an automated job so the dataset refreshes on a cadence
