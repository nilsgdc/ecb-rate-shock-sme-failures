"""
Reusable cleaning / feature-construction pipeline for the ECB-rate / SME-failures study.

Documented stubs — the concrete logic is filled in during the cleaning phase
(notebook 02), once the raw file schemas are known.
"""
import pandas as pd

# --- Analytical constants (justified in the notebooks / README) -------------

# DiD treatment date: first ECB policy-rate hike.
ECB_FIRST_HIKE = "2022-07-01"

# Clean pre-treatment baseline window (deliberately excludes COVID / PGE years).
BASELINE_START = "2015-01-01"
BASELINE_END = "2019-12-31"

# COVID / PGE anomaly window, excluded or treated separately (see README).
COVID_START = "2020-01-01"
COVID_END = "2021-12-31"

# Window over which the credit-intensity ratio is computed to define treatment.
INTENSITY_WINDOW = ("2018-01-01", "2021-12-31")


def credit_intensity_ratio(credit: pd.DataFrame) -> pd.Series:
    """
    Compute, per NAF sector, the ratio of short-term/treasury credit to total
    credit over INTENSITY_WINDOW. This ratio is the basis for classifying
    sectors as treatment (high intensity) vs control (low intensity).

    Parameters
    ----------
    credit : pd.DataFrame
        As returned by data_loader.load_credit_by_sector().

    Returns
    -------
    pd.Series
        Credit-intensity ratio indexed by NAF sector.
    """
    raise NotImplementedError("Implemented in the cleaning phase (notebook 02).")


def assign_treatment(intensity: pd.Series, threshold: float) -> pd.DataFrame:
    """
    Split sectors into treatment / control based on a credit-intensity threshold.

    The threshold is a modelling choice; the analysis tests robustness to
    alternative values (see README "Limitations").

    Parameters
    ----------
    intensity : pd.Series
        Output of credit_intensity_ratio().
    threshold : float
        Cut-off above which a sector is "credit-intensive" (treated).

    Returns
    -------
    pd.DataFrame
        One row per NAF sector with a boolean `treated` column.
    """
    raise NotImplementedError("Implemented in the cleaning phase (notebook 02).")


def drop_covid_window(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Remove the COVID / PGE anomaly window (2020–2021) so it does not contaminate
    the pre-treatment baseline. See the dedicated README section on disentangling
    the rate effect from the PGE rebound.
    """
    raise NotImplementedError("Implemented in the cleaning phase (notebook 02).")


def build_panel() -> pd.DataFrame:
    """
    Assemble the analysis panel: one row per (sector, size class, month), with
    failure counts, treatment flag, post-treatment flag, the DiD interaction,
    ZFRR territorial flag, and control variables.

    Returns
    -------
    pd.DataFrame
        The panel consumed by the DiD regression in notebook 03.
    """
    raise NotImplementedError("Implemented in the cleaning phase (notebook 02).")
