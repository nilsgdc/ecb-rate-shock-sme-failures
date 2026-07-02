-- Department profile: ZFRR intensity, firm stock and failure burden.
-- Three-way join between the department panel, the ZFRR intensity table and
-- the FLORES firm counts, with a failure rate per 1,000 firms.
WITH post AS (
    SELECT
        dept,
        ANY_VALUE(zfrr_share)  AS zfrr_share,
        AVG(failures)          AS avg_failures_post
    FROM read_csv('../data/processed/dept_panel_annual.csv', types = {'dept': 'VARCHAR'})
    WHERE post = 1 AND failures > 0
    GROUP BY dept
)
SELECT
    p.dept,
    ROUND(p.zfrr_share, 2)                                  AS zfrr_share,
    f.firm_count,
    ROUND(p.avg_failures_post, 0)                           AS avg_failures_post,
    ROUND(1000.0 * p.avg_failures_post / f.firm_count, 2)   AS failures_per_1000_firms
FROM post AS p
JOIN read_csv('../data/processed/zfrr_intensity.csv', types = {'dept': 'VARCHAR'}) AS z
  ON p.dept = z.dept
JOIN read_csv('../data/processed/dept_firm_counts.csv', types = {'dept': 'VARCHAR'}) AS f
  ON p.dept = f.dept
ORDER BY failures_per_1000_firms DESC
LIMIT 15;
