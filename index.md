---
layout: default
title: Fragrance Dataset Overview Dashboard
---


**SQL Data Cleaning + Tableau Visualization Project**

This is a data analytics portfolio project that uses MySQL to clean, deduplicate, validate, and transform a raw fragrance dataset. The cleaned data was then visualized in Tableau to summarize fragrance trends by gender, brand, rating, and primary accords.

![Fragrance Dataset Overview Dashboard](assets/images/tableau_final_dashboard.png)

## Project Summary

The goal of this project was to turn messy raw fragrance data into a cleaned and validated dataset that could support dashboard analysis.

The final dashboard highlights:

- Total fragrances in the cleaned dataset
- Average fragrance rating
- Total rating count
- Fragrance distribution by gender
- Top brands by fragrance count
- Highest-rated fragrances with 100+ ratings
- Most common primary accords

## Key Results

- **Total Fragrances:** 69,948
- **Average Rating:** 3.98
- **Total Rating Count:** 14,400,241

## Tools Used

- **MySQL** – data cleaning, deduplication, transformation, and validation
- **Tableau** – dashboard creation and visualization
- **GitHub** – documentation and version control
- **GitHub Pages** – project website

## Project Files

- [Full README](https://github.com/alexko132/fragrance_data_analysis/blob/main/README.md)
- [User Requirements Document PDF](assets/docs/user_requirements_document.pdf)
- [User Requirements Document DOCX](assets/docs/user_requirements_document.docx)
- [Sample Raw Dataset](assets/datasets/raw_fragrance_dataset_sample.csv)
- [Dataset Note](assets/datasets/dataset_note.md)

### SQL Files

- [All SQL Files](https://github.com/alexko132/fragrance_data_analysis/tree/main/assets/sql)
- [Create Raw Table SQL](assets/sql/01_create_raw_table.sql)
- [Import Data SQL](assets/sql/02_import_data.sql)
- [Cleaned View SQL](assets/sql/03_create_cleaned_view.sql)
- [Quality Checks SQL](assets/sql/04_quality_checks.sql)

### Screenshots

- [Project Screenshots](https://github.com/alexko132/fragrance_data_analysis/tree/main/assets/images)
- [Dashboard Screenshot](assets/images/tableau_final_dashboard.png)

## Dataset Note

The full raw dataset is not included in this repository because it exceeds GitHub’s file size limit. A smaller sample CSV is included for preview purposes. The full dataset was processed locally in MySQL to create the final dashboard results.

## View the Repository

For the full project explanation, SQL process, data quality checks, dashboard results, and future improvements, see the [README](https://github.com/alexko132/fragrance_data_analysis/blob/main/README.md).
