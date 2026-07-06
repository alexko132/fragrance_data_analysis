-- 01_create_raw_table.sql
-- Project: Fragrance Dataset Overview Dashboard
-- Purpose: Create the database and raw import table for the fragrance dataset.

CREATE DATABASE IF NOT EXISTS fragrance_dataset;

USE fragrance_dataset;

DROP TABLE IF EXISTS fra_perfumes_raw;

CREATE TABLE fra_perfumes_raw (
    `Name` TEXT,
    `Gender` VARCHAR(255),
    `Rating Value` VARCHAR(50),
    `Rating Count` VARCHAR(50),
    `Main Accords` TEXT,
    `Perfumers` TEXT,
    `Description` TEXT,
    `url` VARCHAR(2048)
);

-- Notes:
-- The raw table stores most imported fields as text because the data is cleaned later
-- in the cleaned SQL view. Rating Value and Rating Count are intentionally imported
-- as text first so commas, blanks, N/A values, and other messy values can be handled
-- safely during transformation.
