"""Cleaning and feature construction for the ECB-rate / SME-failures study."""
import pandas as pd

# DiD treatment date: first ECB policy-rate hike.
ECB_FIRST_HIKE = "2022-07-01"

# Pre-treatment baseline window (excludes the COVID / PGE years).
BASELINE_START = "2015-01-01"
BASELINE_END = "2019-12-31"

# COVID / PGE anomaly window, excluded from the baseline.
COVID_START = "2020-01-01"
COVID_END = "2021-12-31"

# Window over which the credit-intensity ratio is computed.
INTENSITY_WINDOW = ("2018-01-01", "2021-12-31")


def credit_intensity_ratio(credit: pd.DataFrame) -> pd.Series:
    """
    Ratio of short-term/treasury credit to total credit per NAF sector over
    INTENSITY_WINDOW. Basis for splitting sectors into treatment and control.
    """
    raise NotImplementedError


def assign_treatment(intensity: pd.Series, threshold: float) -> pd.DataFrame:
    """
    Split sectors into treatment/control on a credit-intensity threshold.
    Returns one row per NAF sector with a boolean `treated` column.
    """
    raise NotImplementedError


def drop_covid_window(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Remove the 2020–2021 COVID/PGE window so it does not contaminate the baseline."""
    raise NotImplementedError


def build_panel() -> pd.DataFrame:
    """
    Assemble the analysis panel: one row per (sector, size class, month) with failure
    counts, treatment flag, post-treatment flag, the DiD interaction, the ZFRR flag,
    and control variables.
    """
    raise NotImplementedError
