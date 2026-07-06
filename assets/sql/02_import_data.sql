-- 02_import_data.sql
-- Project: Fragrance Dataset Overview Dashboard
-- Purpose: Import the raw fragrance CSV into the raw MySQL table.

USE fragrance_dataset;

-- Optional: Clear the raw table before importing.
TRUNCATE TABLE fra_perfumes_raw;

-- IMPORTANT:
-- Replace the file path below with the location of your CSV file on your computer.
-- Example for macOS:
-- '/Users/yourname/Downloads/raw_fragrance_dataset.csv'
--
-- Example for Windows:
-- 'C:/Users/yourname/Downloads/raw_fragrance_dataset.csv'
--
-- If you are testing with the GitHub sample file, use the path to:
-- assets/datasets/raw_fragrance_dataset_sample.csv
--
-- The full raw dataset was imported locally. The GitHub repository includes only
-- a sample CSV because the full file exceeds GitHub's file size limit.

LOAD DATA LOCAL INFILE '/path/to/your/raw_fragrance_dataset.csv'
INTO TABLE fra_perfumes_raw
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    `Name`,
    `Gender`,
    `Rating Value`,
    `Rating Count`,
    `Main Accords`,
    `Perfumers`,
    `Description`,
    `url`
);

-- If LOAD DATA LOCAL INFILE is disabled in MySQL Workbench, use:
-- Server > Data Import, or use the Table Data Import Wizard.
--
-- This SQL file is included to document the intended import structure and
-- expected CSV column order.
