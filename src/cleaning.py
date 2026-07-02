"""Cleaning and feature construction for the ECB-rate / SME-failures study."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# DiD treatment date: first ECB policy-rate hike.
ECB_FIRST_HIKE = pd.Timestamp("2022-07-01")

# Pre-treatment baseline window (excludes the COVID / PGE years). Used for the
# monthly visualisations only; the regressions run on the annual panel below.
BASELINE_START = pd.Timestamp("2015-01-01")
BASELINE_END = pd.Timestamp("2019-12-31")

# COVID / PGE anomaly window, shaded/excluded in the monthly views.
COVID_START = pd.Timestamp("2020-01-01")
COVID_END = pd.Timestamp("2022-06-30")

# --- Annual non-overlapping design (used for all regressions) ---------------
# The dependent variable is a 12-month rolling cumulative; sampled monthly it is
# heavily autocorrelated and its post-hike values are contaminated by pre-hike
# months. Taking the December value of each year gives a non-overlapping annual
# series (= calendar-year total) and a clean break:
#   - baseline years 2015-2019,
#   - 2020-2022 dropped (COVID/PGE + the 2022 transition year, whose December
#     cumulative still straddles the July-2022 hike),
#   - post years 2023 onward (December cumulative then lies fully after the hike).
BASELINE_YEARS = (2015, 2019)
POST_YEAR_START = 2023

# Years over which the bank-credit-dependence ratio is averaged to classify sectors.
DEPENDENCE_WINDOW = (2018, 2021)

# Failure-sector (NAF section) -> FIBEN debt sub-sectors that compose it.
# Most match directly; industry and personal services aggregate two FIBEN sectors.
SECTOR_DEBT_MAP = {
    "AZ": ["AZ"], "BE": ["C", "DE"], "FZ": ["FZ"], "G": ["G"], "H": ["H"],
    "I": ["I"], "JZ": ["JZ"], "MN": ["MN"], "PS": ["PQ", "RS"],
}


def bank_credit_dependence(debt_structure: pd.DataFrame) -> pd.Series:
    """
    Share of bank debt in total financial debt per analysis sector, averaged over
    DEPENDENCE_WINDOW. For sectors that map to two FIBEN sub-sectors (industry,
    personal services) the sub-sector ratios are averaged (simple mean, an
    approximation since debt weights are not available at this granularity).

    Parameters
    ----------
    debt_structure : pd.DataFrame
        Tidy frame from data_loader.load_sector_debt_structure().

    Returns
    -------
    pd.Series
        Bank-credit-dependence (%) indexed by analysis-sector code.
    """
    be = debt_structure[
        (debt_structure["ratio_code"] == "BE")
        & (debt_structure["year"].between(*DEPENDENCE_WINDOW))
    ]
    by_sub = be.groupby("sector")["value"].mean()
    return pd.Series(
        {sec: by_sub.reindex(parts).mean() for sec, parts in SECTOR_DEBT_MAP.items()},
        name="bank_dependence",
    )


def assign_treatment(dependence: pd.Series, threshold=None) -> pd.DataFrame:
    """
    Split sectors into treatment/control on a bank-credit-dependence threshold
    (default: the median). Returns one row per sector with the dependence value
    and a boolean `treated` column.
    """
    if threshold is None:
        threshold = dependence.median()
    out = dependence.to_frame()
    out["treated"] = out["bank_dependence"] >= threshold
    return out.sort_values("bank_dependence", ascending=False)


def build_panel(failures: pd.DataFrame, treatment: pd.DataFrame) -> pd.DataFrame:
    """
    Assemble the analysis panel: one row per (sector, month), with the failure count,
    treatment/post/DiD indicators, and window flags.

    `in_sample` keeps the clean baseline (2015-2019) and the post-treatment period,
    dropping the COVID/PGE window (2020-01 to 2022-06).
    """
    panel = failures.merge(
        treatment[["treated"]], left_on="sector", right_index=True, how="inner"
    )
    panel["post"] = (panel["date"] >= ECB_FIRST_HIKE).astype(int)
    panel["treated"] = panel["treated"].astype(int)
    panel["did"] = panel["post"] * panel["treated"]
    panel["in_baseline"] = panel["date"].between(BASELINE_START, BASELINE_END)
    panel["in_covid"] = panel["date"].between(COVID_START, COVID_END)
    panel["in_sample"] = panel["in_baseline"] | (panel["date"] >= ECB_FIRST_HIKE)
    return panel.sort_values(["sector", "date"]).reset_index(drop=True)


def zfrr_intensity_by_department(frr: pd.DataFrame, col: str = "classified") -> pd.Series:
    """
    Share of a department's communes classified FRR (treatment intensity).
    `col` selects the definition: "classified" = FRR socle or + (codes 4-5, default),
    "frr_any" = any FRR status (codes 1-5, used as a robustness check).
    """
    return frr.groupby("dept")[col].mean().rename("zfrr_share")


def build_dept_panel(dept_failures: pd.DataFrame, intensity: pd.Series,
                     threshold=None) -> pd.DataFrame:
    """
    Department-level panel for the territorial analysis: one row per (dept, month)
    with the failure count, ZFRR intensity, treatment/post/DiD indicators and window
    flags. Treatment = departments with above-median ZFRR intensity.
    """
    if threshold is None:
        threshold = intensity.median()
    panel = dept_failures.merge(intensity, left_on="dept", right_index=True, how="inner")
    panel["treated"] = (panel["zfrr_share"] >= threshold).astype(int)
    panel["post"] = (panel["date"] >= ECB_FIRST_HIKE).astype(int)
    panel["did"] = panel["post"] * panel["treated"]
    panel["in_baseline"] = panel["date"].between(BASELINE_START, BASELINE_END)
    panel["in_sample"] = panel["in_baseline"] | (panel["date"] >= ECB_FIRST_HIKE)
    return panel.sort_values(["dept", "date"]).reset_index(drop=True)


def annualize(panel: pd.DataFrame, unit_col: str) -> pd.DataFrame:
    """
    Collapse a monthly 12-month-cumulative panel to one non-overlapping annual
    observation per unit (each December = that calendar year's total), and define
    the annual treatment timing.

    Keeps the 2015-2019 baseline and 2023+ post years; drops 2020-2022. Adds:
    year, post, in_baseline, in_sample, did. Treatment/intensity columns are
    carried over from the monthly panel.
    """
    dec = panel[panel["date"].dt.month == 12].copy()
    dec["year"] = dec["date"].dt.year
    dec["post"] = (dec["year"] >= POST_YEAR_START).astype(int)
    dec["in_baseline"] = dec["year"].between(*BASELINE_YEARS)
    dec["in_sample"] = dec["in_baseline"] | (dec["year"] >= POST_YEAR_START)
    dec["did"] = dec["post"] * dec["treated"]
    return dec.sort_values([unit_col, "year"]).reset_index(drop=True)


def wild_cluster_bootstrap_p(data: pd.DataFrame, full_formula: str,
                             restricted_formula: str, param: str,
                             cluster_col: str, n_boot: int = 1999,
                             seed: int = 12345) -> dict:
    """
    Wild cluster restricted (WCR) bootstrap p-value for a single coefficient,
    following Cameron, Gelbach & Miller (2008). Designed for few clusters, where
    cluster-robust asymptotics are unreliable (e.g. the 9-sector analysis).

    Imposes the null on `param` (restricted model), resamples cluster-level
    residuals with Rademacher (+/-1) weights, and compares bootstrap t-statistics
    to the observed one.

    Returns {'coef', 't_obs', 'p_boot', 'n_boot', 'n_clusters'}.
    """
    rng = np.random.default_rng(seed)
    full = smf.ols(full_formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data[cluster_col]})
    t_obs = full.params[param] / full.bse[param]

    restr = smf.ols(restricted_formula, data=data).fit()
    fitted = restr.fittedvalues.to_numpy()
    resid = restr.resid.to_numpy()
    depvar = full_formula.split("~")[0].strip()

    clusters = data[cluster_col].to_numpy()
    uniq = pd.unique(clusters)
    count = 0
    boot = data.copy()
    for _ in range(n_boot):
        w = dict(zip(uniq, rng.choice([-1.0, 1.0], size=len(uniq))))
        wv = np.array([w[c] for c in clusters])
        boot[depvar] = fitted + resid * wv
        fit_b = smf.ols(full_formula, data=boot).fit(
            cov_type="cluster", cov_kwds={"groups": boot[cluster_col]})
        t_b = fit_b.params[param] / fit_b.bse[param]
        if abs(t_b) >= abs(t_obs):
            count += 1
    return {
        "coef": float(full.params[param]),
        "t_obs": float(t_obs),
        "p_boot": (count + 1) / (n_boot + 1),
        "n_boot": n_boot,
        "n_clusters": int(len(uniq)),
    }
