"""
Centralised loading functions for all datasets of the ECB-rate / SME-failures study.

These are documented stubs: the exact parsing logic depends on the precise file
formats downloaded from Banque de France Webstat, data.gouv.fr (ZFRR, SIRENE) and
INSEE, which are filled in during the data-ingestion phase (notebook 01).

Expected raw layout (see README "Data sources"):

    data/raw/
    ├── banque_de_france/   # credit by NAF sector + failures by sector & size (monthly)
    ├── bce_rates/          # ECB policy-rate history
    ├── zfrr/               # ZFRR / ZFRR+ municipality list
    └── sirene/             # SIRENE business registry (SME counts per sector)
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

BDF_DIR = RAW_DIR / "banque_de_france"
RATES_DIR = RAW_DIR / "bce_rates"
ZFRR_DIR = RAW_DIR / "zfrr"
SIRENE_DIR = RAW_DIR / "sirene"


def load_credit_by_sector() -> pd.DataFrame:
    """
    Load monthly credit outstanding by NAF sector (treasury vs total) from
    Banque de France Webstat.

    Returns
    -------
    pd.DataFrame
        Indexed by (date, naf_sector), with columns for treasury credit and
        total credit outstanding. Used to build the credit-intensity ratio
        that defines the treatment group.
    """
    raise NotImplementedError("Implemented in the data-ingestion phase (notebook 01).")


def load_failures() -> pd.DataFrame:
    """
    Load monthly business-failure counts by NAF sector and firm-size class
    (Banque de France).

    'Failure' = opening of a redressement or liquidation judiciaire only
    (see README). Excludes voluntary closures, deregistrations, disposals.

    Returns
    -------
    pd.DataFrame
        Indexed by (date, naf_sector, size_class), with a failure-count column.
        This is the dependent variable of the DiD model.
    """
    raise NotImplementedError("Implemented in the data-ingestion phase (notebook 01).")


def load_ecb_rates() -> pd.DataFrame:
    """
    Load the ECB policy-rate history (main refinancing / deposit facility rate).

    Returns
    -------
    pd.DataFrame
        Date-indexed policy rates. The first hike (July 2022) is the DiD
        treatment date.
    """
    raise NotImplementedError("Implemented in the data-ingestion phase (notebook 01).")


def load_zfrr_communes() -> pd.DataFrame:
    """
    Load the list of municipalities classified ZFRR / ZFRR+ (data.gouv.fr).

    Returns
    -------
    pd.DataFrame
        One row per commune (INSEE code), with the ZFRR classification flag,
        used for the territorial-equity interaction term.
    """
    raise NotImplementedError("Implemented in the data-ingestion phase (notebook 01).")


def load_sirene_sme_counts() -> pd.DataFrame:
    """
    Load SME counts per NAF sector from the SIRENE registry, used to weight
    failure rates by the number of SMEs at risk in each sector.

    Returns
    -------
    pd.DataFrame
        SME counts indexed by NAF sector (and optionally commune/region).
    """
    raise NotImplementedError("Implemented in the data-ingestion phase (notebook 01).")
