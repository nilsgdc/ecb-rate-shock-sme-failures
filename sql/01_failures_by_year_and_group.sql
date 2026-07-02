-- Annual PME failures by treatment group.
-- Joins the annual panel with the sector treatment table and pivots the
-- clean sample (baseline 2015-2019, post 2023+) into one row per year.
SELECT
    p.year,
    SUM(CASE WHEN t.treated THEN p.failures END)      AS failures_treated,
    SUM(CASE WHEN NOT t.treated THEN p.failures END)  AS failures_control,
    ROUND(SUM(p.failures))                            AS failures_total
FROM read_csv('../data/processed/sector_panel_annual.csv') AS p
JOIN read_csv('../data/processed/treatment.csv') AS t
  ON p.sector = t.sector
WHERE p.in_sample
GROUP BY p.year
ORDER BY p.year;
