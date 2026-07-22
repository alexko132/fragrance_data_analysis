# Fragrance Dataset Overview Dashboard

**SQL Data Cleaning + Tableau Visualization Project**

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

| Check | Rule | Result |
|---|---|---|
| Row count check | Confirms the total row count of the cleaned view | 69,948 rows |
| Duplicate URL check | Should return 0 rows after deduplication | Passed (0 duplicates) |
| Missing cleaned perfume name check | Cleaned names should not become missing if raw data had usable values | Passed (0 rows) |
| Missing cleaned brand check | Cleaned brands should not become missing if raw data had usable values | Passed (0 rows) |
| Missing cleaned accords check | Cleaned accords should not become missing if raw data had usable values | Passed (0 rows) |
| Invalid gender value check | Gender must only be Men, Women, or Unisex | Passed (0 invalid values) |
| Invalid rating value check | Rating Value must be between 0 and 5 | Passed (0 invalid values) |
| Invalid rating count check | Rating Count cannot be negative | Passed (0 invalid values) |

All checks passed, confirming the cleaned dataset was ready to support the recommendations in Section 9.

---

## 7. Dashboard Overview

**Title:** Fragrance Dataset Overview
**Subtitle:** Cleaned fragrance data from MySQL visualized in Tableau

**KPIs:**

- **Total Fragrances:** 69,948
- **Average Rating:** 3.98 — calculated from fragrances with valid numeric rating values; null or invalid rating values were converted to NULL during cleaning and excluded from the average
- **Total Rating Count:** 14,400,241

**Visualizations:**

- Fragrances by Gender (bar chart)
- Top Brands by Fragrance Count (bar chart)
- Top Rated Fragrances with 100+ Ratings (bar chart)
- Most Common Primary Accords (treemap)

Each visualization was chosen to answer one of the business questions in Section 2 directly — the goal was a dashboard a stakeholder could read in under a minute and walk away from with a clear next question, not a wall of exploratory charts.

---

## 8. Key Results

**Fragrances by Gender**

| Gender | Fragrance Count |
|---|---|
| Unisex | 29,607 |
| Women | 28,069 |
| Men | 12,269 |

> Note: The gender breakdown totals 69,945, while the dataset contains 69,948 fragrances. The remaining 3 records had null or unclassified gender values after cleaning, since the gender standardization rule only assigns records to Men, Women, or Unisex when the raw gender value maps clearly to one of those categories.

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

---

## 10. Project Evidence / Screenshots

The `assets/images/` folder documents each stage of the project so the work can be verified without re-running the SQL:

- `raw_data_preview_part_1.png` and `raw_data_preview_part_2.png` – original raw table before cleaning
- `deduped_table_preview.png` – deduplicated table
- `cleaned_view_preview_part_1.png`, `cleaned_view_preview_part_2.png`, and `cleaned_view_preview_part_3.png` – cleaned SQL view used for Tableau
- `row_count_check.png` – confirms the cleaned row count
- `duplicate_url_check.png` – confirms duplicate URLs were removed
- `missing_names_check.png` – validates cleaned perfume names
- `missing_brands_check.png` – validates cleaned brands
- `missing_accords_check.png` – validates cleaned accords
- `invalid_gender_check.png` – validates standardized gender values
- `invalid_rating_value_check.png` – validates rating values are between 0 and 5
- `invalid_rating_count_check.png` – validates rating counts are not negative

---

## 11. Project Files

```
fragrance_data_analysis/
│
├── README.md
├── index.md
├── _config.yml
│
├── assets/
│   ├── datasets/
│   │   ├── raw_fragrance_dataset_sample.csv
│   │   └── dataset_note.md
│   │
│   ├── docs/
│   │   ├── user_requirements_document.docx
│   │   └── user_requirements_document.pdf
│   │
│   ├── images/
│   │   ├── tableau_final_dashboard.png
│   │   ├── raw_data_preview_part_1.png
│   │   ├── raw_data_preview_part_2.png
│   │   ├── deduped_table_preview.png
│   │   ├── cleaned_view_preview_part_1.png
│   │   ├── cleaned_view_preview_part_2.png
│   │   ├── cleaned_view_preview_part_3.png
│   │   ├── row_count_check.png
│   │   ├── duplicate_url_check.png
│   │   ├── missing_names_check.png
│   │   ├── missing_brands_check.png
│   │   ├── missing_accords_check.png
│   │   ├── invalid_gender_check.png
│   │   ├── invalid_rating_value_check.png
│   │   └── invalid_rating_count_check.png
│   │
│   └── sql/
│       ├── 01_create_raw_table.sql
│       ├── 02_import_data.sql
│       ├── 03_create_cleaned_view.sql
│       └── 04_quality_checks.sql
```

> The full raw dataset (`raw_fragrance_dataset.csv`) is not included in the repository due to GitHub file size limits. Only a sample is provided in `assets/datasets/`.

---

## 12. How to Reproduce

1. Review the sample raw dataset in `assets/datasets/` to understand the raw data structure.
2. Note that the sample CSV is included only to show the raw data structure — it will not reproduce the exact final dashboard numbers.
3. To reproduce the exact final dashboard numbers, the full raw dataset is needed.
4. The full raw dataset was processed locally in MySQL because it was too large for GitHub.
5. Run the SQL files in `assets/sql/` in order: create the raw table, import the data, create the cleaned view (`vw_fragrances_cleaned`), and run the quality checks.
6. Connect Tableau to the cleaned view (or an exported cleaned dataset).
7. Build the dashboard visuals: KPIs, gender bar chart, top brands chart, top rated fragrances chart, and the primary accords treemap.

> The sample CSV is included to show the structure of the raw data. Reproducing the exact dashboard totals requires the full raw dataset, which was processed locally because it was too large for GitHub.

---

## 13. Business/Portfolio Value

This project was structured the way a consulting or product analytics engagement would be: start from a business problem (an unreliable dataset that can't safely inform decisions), build the technical foundation to solve it, and end with recommendations a leadership team could act on. That included:

- Identifying why the raw data was unsafe to use for decision-making in its original form
- SQL data cleaning, deduplication, and transformation to build a trustworthy dataset
- Repeatable data validation checks, treated as a gate before any finding could be presented as reliable
- Dashboard design and KPI selection aimed at the specific questions a stakeholder would ask
- Translating each data finding into a recommendation or a flagged follow-up question, rather than stopping at description
- Being explicit about the limits of the data (scraped review data vs. verified sales/market data) so recommendations aren't overstated

These are the same steps required in a real business setting when raw operational or scraped data needs to be converted into a reliable reporting layer that a team can actually make decisions from.

---

## 14. Future Improvements

- Add additional accord columns (beyond Main Accord 1–5) or model accords in a normalized long format for deeper analysis.
- Analyze the relationship between rating value, rating count, and gender category.
- Add brand-level average ratings to compare brand quality, not just volume — directly addressing the caveat in Finding 2.
- Validate the Men's fragrance gap (Finding 1) against an external retail or sales dataset.
- Automate the cleaning pipeline with stored procedures or a scheduled ETL job.
- Publish the dashboard to Tableau Public and add interactive filters (brand, gender, accord).
