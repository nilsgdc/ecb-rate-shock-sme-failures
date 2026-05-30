"""Cleaning and feature construction for the ECB-rate / SME-failures study."""
import pandas as pd

# DiD treatment date: first ECB policy-rate hike.
ECB_FIRST_HIKE = pd.Timestamp("2022-07-01")

# Pre-treatment baseline window (excludes the COVID / PGE years).
BASELINE_START = pd.Timestamp("2015-01-01")
BASELINE_END = pd.Timestamp("2019-12-31")

# COVID / PGE anomaly window, excluded from the analysis sample.
# Extended to the hike so the rebound ramp does not contaminate the pre period.
COVID_START = pd.Timestamp("2020-01-01")
COVID_END = pd.Timestamp("2022-06-30")

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
    personal services) the sub-sector ratios are averaged (simple mean — an
    approximation, since debt weights are not available at this granularity).

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
