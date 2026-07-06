/*

Data Cleaning Steps:
1. Add necessary columns and rename existing columns
2. Clean values for each column

*/

USE fragrance_dataset;

CREATE OR REPLACE VIEW vw_fragrances_cleaned AS 
SELECT
    url AS `URL`,

    `Name` AS `Raw Name`,

    CASE
        WHEN clean_perfume_from_url IS NULL
          OR TRIM(clean_perfume_from_url) = ''
        THEN NULLIF(TRIM(`Name`), '')
        ELSE clean_perfume_from_url
    END AS `Perfume`,

    TRIM(
        REPLACE(
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(TRIM(url), '/perfume/', -1),
                '/',
                1
            ),
            '-',
            ' '
        )
    ) AS `Brand`,

    `Gender` AS `Raw Gender`,

    CASE
        WHEN LOWER(TRIM(`Gender`)) LIKE '%women and men%' THEN 'Unisex'
        WHEN LOWER(TRIM(`Gender`)) LIKE '%men and women%' THEN 'Unisex'
        WHEN LOWER(TRIM(`Gender`)) LIKE '%unisex%' THEN 'Unisex'
        WHEN LOWER(TRIM(`Gender`)) LIKE '%women%' THEN 'Women'
        WHEN LOWER(TRIM(`Gender`)) LIKE '%female%' THEN 'Women'
        WHEN LOWER(TRIM(`Gender`)) LIKE '%men%' THEN 'Men'
        WHEN LOWER(TRIM(`Gender`)) LIKE '%male%' THEN 'Men'
        ELSE NULL
    END AS `Gender`,

    `Rating Value` AS `Raw Rating Value`,

    CASE
        WHEN clean_rating_value_text IS NULL
          OR TRIM(clean_rating_value_text) = ''
        THEN NULL
        WHEN clean_rating_value_text REGEXP '^[0-9]+([.][0-9]+)?$'
        THEN CAST(clean_rating_value_text AS DECIMAL(4,2))
        ELSE NULL
    END AS `Rating Value`,

    `Rating Count` AS `Raw Rating Count`,

    CASE
        WHEN clean_rating_count_text IS NULL
          OR TRIM(clean_rating_count_text) = ''
        THEN NULL
        WHEN clean_rating_count_text REGEXP '^[0-9]+$'
        THEN CAST(clean_rating_count_text AS UNSIGNED)
        ELSE NULL
    END AS `Rating Count`,

    CASE
        WHEN `Main Accords` IS NULL
          OR TRIM(`Main Accords`) = ''
          OR TRIM(`Main Accords`) = '[]'
        THEN NULL
        ELSE `Main Accords`
    END AS `Raw Main Accords`,

    NULLIF(TRIM(SUBSTRING_INDEX(clean_accords, ',', 1)), '') AS `Main Accord 1`,

    NULLIF(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(clean_accords, ',', 2), ',', -1)), '') AS `Main Accord 2`,

    NULLIF(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(clean_accords, ',', 3), ',', -1)), '') AS `Main Accord 3`,

    NULLIF(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(clean_accords, ',', 4), ',', -1)), '') AS `Main Accord 4`,

    NULLIF(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(clean_accords, ',', 5), ',', -1)), '') AS `Main Accord 5`

FROM (
    SELECT
        *,

        TRIM(
            REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        SUBSTRING_INDEX(TRIM(url), '/', -1),
                        '\\.html$',
                        ''
                    ),
                    '-[0-9]+$',
                    ''
                ),
                '-',
                ' '
            )
        ) AS clean_perfume_from_url,

        CASE
            WHEN `Rating Value` IS NULL
              OR TRIM(`Rating Value`) = ''
              OR UPPER(TRIM(`Rating Value`)) = 'N/A'
            THEN NULL
            ELSE REPLACE(TRIM(`Rating Value`), ',', '.')
        END AS clean_rating_value_text,

        CASE
            WHEN `Rating Count` IS NULL
              OR TRIM(`Rating Count`) = ''
              OR UPPER(TRIM(`Rating Count`)) = 'N/A'
            THEN NULL
            ELSE NULLIF(
                REGEXP_REPLACE(TRIM(`Rating Count`), '[^0-9]', ''),
                ''
            )
        END AS clean_rating_count_text,

        CASE
            WHEN `Main Accords` IS NULL
              OR TRIM(`Main Accords`) = ''
              OR TRIM(`Main Accords`) = '[]'
            THEN NULL
            ELSE REPLACE(
                REPLACE(
                    REPLACE(TRIM(`Main Accords`), '[', ''),
                ']', ''),
            '''', '')
        END AS clean_accords

    FROM fra_perfumes_raw_deduped
) AS cleaned;