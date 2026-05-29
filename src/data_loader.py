"""
Loading functions for the study's datasets.

Expected raw layout:

    data/raw/
    ├── banque_de_france/   sector debt structure (FIBEN, annual) + failures by sector & size (monthly)
    ├── bce_rates/          ECB policy-rate history
    ├── zfrr/               ZFRR / ZFRR+ municipality list
    └── sirene/             SME counts per sector
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

BDF_DIR = RAW_DIR / "banque_de_france"
RATES_DIR = RAW_DIR / "bce_rates"
ZFRR_DIR = RAW_DIR / "zfrr"
SIRENE_DIR = RAW_DIR / "sirene"


def load_sector_debt_structure() -> pd.DataFrame:
    """
    Annual FIBEN balance-sheet ratios by NAF sector (Banque de France): share of bank
    debt in total financial debt, financial leverage, working-capital need.

    Indexed by (year, naf_sector). The bank-debt share, averaged over 2018–2021, defines
    the treatment group.
    """
    raise NotImplementedError


def load_failures() -> pd.DataFrame:
    """
    Monthly business-failure counts by NAF sector and firm-size class, Banque de France.

    A failure is the opening of a redressement or liquidation judiciaire only. Indexed by
    (date, naf_sector, size_class); the failure count is the dependent variable.
    """
    raise NotImplementedError


def load_ecb_rates() -> pd.DataFrame:
    """
    ECB policy rates (main refinancing and deposit facility), date-indexed.

    The first hike (July 2022) is the difference-in-differences treatment date.
    """
    raise NotImplementedError


def load_zfrr_communes() -> pd.DataFrame:
    """
    Municipalities classified ZFRR / ZFRR+, one row per commune (INSEE code) with the
    classification flag. Feeds the territorial interaction term.
    """
    raise NotImplementedError


def load_sirene_sme_counts() -> pd.DataFrame:
    """
    SME counts per NAF sector, used to weight failure rates by the number of SMEs at risk.
    """
    raise NotImplementedError
