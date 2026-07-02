-- The 2x2 difference-in-differences table in one query.
-- Averages log(1 + failures) by treatment group and period, then the outer
-- query lines up the four cells and computes the raw DiD estimate.
WITH cells AS (
    SELECT
        t.treated,
        p.post,
        AVG(LN(1 + p.failures)) AS mean_log_failures
    FROM read_csv('../data/processed/sector_panel_annual.csv') AS p
    JOIN read_csv('../data/processed/treatment.csv') AS t
      ON p.sector = t.sector
    WHERE p.in_sample
    GROUP BY t.treated, p.post
)
SELECT
    MAX(CASE WHEN treated AND post = 0 THEN mean_log_failures END)     AS treated_before,
    MAX(CASE WHEN treated AND post = 1 THEN mean_log_failures END)     AS treated_after,
    MAX(CASE WHEN NOT treated AND post = 0 THEN mean_log_failures END) AS control_before,
    MAX(CASE WHEN NOT treated AND post = 1 THEN mean_log_failures END) AS control_after,
    (MAX(CASE WHEN treated AND post = 1 THEN mean_log_failures END)
     - MAX(CASE WHEN treated AND post = 0 THEN mean_log_failures END))
    - (MAX(CASE WHEN NOT treated AND post = 1 THEN mean_log_failures END)
       - MAX(CASE WHEN NOT treated AND post = 0 THEN mean_log_failures END)) AS did_raw
FROM cells;
