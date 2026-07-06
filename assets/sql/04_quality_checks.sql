/*
Data Quality Tests:

1. Total Row Count --- (Passed)
2. Duplicate URLs ---(Passed)
3. Missing Categories (Name, Brand, Accords), excluding columns already missing in raw data ---(Passed)
4. Valid Values in Categories (Gender, Rating Value, Rating Count) 


Row Count - 69948

Duplicate Count = 0

Missing Count = 0

Invalid Value Count = 0
*/

-- 1. Row Count Check
SELECT COUNT(*) AS total_rows
FROM vw_fragrances_cleaned;

-- 2. Duplicate URL check
SELECT
    `URL`,
    COUNT(*) AS duplicate_count
FROM vw_fragrances_cleaned
GROUP BY `URL`
HAVING COUNT(*) > 1;

-- 3. Missing Categories check
	
    -- a. Missing Name check
SELECT
    COUNT(*) AS missing_cleaned_names_not_missing_in_raw
FROM vw_fragrances_cleaned
WHERE `Raw Name` IS NOT NULL
  AND TRIM(`Raw Name`) <> ''
  AND (
        `Perfume` IS NULL
        OR TRIM(`Perfume`) = ''
      );
      
	-- b. Missing Brand check 
SELECT
    COUNT(*) AS missing_cleaned_brands_not_missing_in_raw
FROM (
    SELECT
        `URL`,
        TRIM(
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(TRIM(`URL`), '/perfume/', -1),
                '/',
                1
            )
        ) AS raw_brand_from_url,
        `Brand`
    FROM vw_fragrances_cleaned
    WHERE `URL` LIKE '%/perfume/%'
) AS brand_check
WHERE raw_brand_from_url IS NOT NULL
  AND TRIM(raw_brand_from_url) <> ''
  AND (
        `Brand` IS NULL
        OR TRIM(`Brand`) = ''
      );
      
      -- c. Missing Accords Check 
SELECT
    COUNT(*) AS missing_cleaned_accords_not_missing_in_raw
FROM vw_fragrances_cleaned
WHERE `Raw Main Accords` IS NOT NULL
  AND TRIM(`Raw Main Accords`) <> ''
  AND (
        (`Main Accord 1` IS NULL OR TRIM(`Main Accord 1`) = '')
    AND (`Main Accord 2` IS NULL OR TRIM(`Main Accord 2`) = '')
    AND (`Main Accord 3` IS NULL OR TRIM(`Main Accord 3`) = '')
    AND (`Main Accord 4` IS NULL OR TRIM(`Main Accord 4`) = '')
    AND (`Main Accord 5` IS NULL OR TRIM(`Main Accord 5`) = '')
      );
      
-- 4. Categories Validity Check
		
        -- a. Valid Gender Values Check 
SELECT
    COUNT(*) AS invalid_gender_count
FROM vw_fragrances_cleaned
WHERE `Gender` NOT IN ('Men', 'Women', 'Unisex')
  AND `Gender` IS NOT NULL;
  
		-- b. Valid Rating Value Check 
SELECT
    COUNT(*) AS invalid_rating_value_count
FROM vw_fragrances_cleaned
WHERE `Rating Value` < 0
   OR `Rating Value` > 5;
   
		-- c. Valid Rating Count Check
SELECT
    COUNT(*) AS invalid_rating_count_count
FROM vw_fragrances_cleaned
WHERE `Rating Count` < 0;
        