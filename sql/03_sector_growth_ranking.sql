-- Post-hike failure growth by sector, against its own baseline.
-- Window functions: the baseline mean is computed per sector with a
-- partitioned AVG, then sectors are ranked by their relative increase.
WITH annual AS (
    SELECT
        p.sector,
        t.label,
        t.bank_dependence,
        p.year,
        p.failures,
        AVG(CASE WHEN p.in_baseline THEN p.failures END)
            OVER (PARTITION BY p.sector) AS baseline_mean
    FROM read_csv('../data/processed/sector_panel_annual.csv') AS p
    JOIN read_csv('../data/processed/treatment.csv') AS t
      ON p.sector = t.sector
    WHERE p.in_sample
)
SELECT
    sector,
    label,
    bank_dependence,
    ROUND(AVG(failures), 0)                                   AS post_mean,
    ROUND(ANY_VALUE(baseline_mean), 0)                        AS baseline_mean,
    ROUND(100.0 * (AVG(failures) / ANY_VALUE(baseline_mean) - 1), 1) AS growth_pct,
    RANK() OVER (ORDER BY AVG(failures) / ANY_VALUE(baseline_mean) DESC) AS rank_by_growth
FROM annual
WHERE year >= 2023
GROUP BY sector, label, bank_dependence
ORDER BY rank_by_growth;
