"""
Loading functions for the study's datasets.

Expected raw layout:

    data/raw/
    ├── banque_de_france/   sector debt structure (FIBEN, annual) + failures by sector & size (monthly)
    ├── bce_rates/          ECB policy-rate history
    ├── zfrr/               ZFRR / ZFRR+ municipality list
    └── sirene/             SME counts per sector

The Banque de France files are SDMX long exports (";"-separated, UTF-8 BOM,
decimal comma). They contain the whole DIREN dataset; the loaders filter to the
combinations the study needs.
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

BDF_DIR = RAW_DIR / "banque_de_france"
RATES_DIR = RAW_DIR / "bce_rates"
ZFRR_DIR = RAW_DIR / "zfrr"
SIRENE_DIR = RAW_DIR / "sirene"

# NAF-section labels used across the project (Banque de France aggregation).
SECTOR_LABELS = {
    "AZ": "Agriculture",
    "BE": "Industry",
    "FZ": "Construction",
    "G": "Trade & auto repair",
    "H": "Transport & storage",
    "I": "Accommodation & food",
    "JZ": "Information & communication",
    "MN": "Business services",
    "PS": "Education, health, personal services",
}


def _read_bdf(path: Path) -> pd.DataFrame:
    """Read a Banque de France SDMX long CSV with the right encoding/separator."""
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
    df["value"] = (
        df["obs_value"].str.replace(" ", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    return df


def load_failures() -> pd.DataFrame:
    """
    Monthly PME business failures by NAF sector (France), Banque de France.

    'Failure' = redressement or liquidation judiciaire only. The series is the
    12-month rolling cumulative count (DIREN measure 03). Returns a tidy frame
    with columns: date, sector, sector_label, failures.
    """
    df = _read_bdf(BDF_DIR / "failures_by_sector_size.csv")
    df = df[
        (df["REF_AREA"] == "FR")
        & (df["DIREN_TAILLENT"] == "PM")
        & (df["DIREN_SECTACT"] != "ZZ")
    ].copy()
    df["date"] = pd.to_datetime(df["time_period"], format="%Y-%m")
    out = df[["date", "DIREN_SECTACT", "value"]].rename(
        columns={"DIREN_SECTACT": "sector", "value": "failures"}
    )
    out["sector_label"] = out["sector"].map(SECTOR_LABELS)
    return out.sort_values(["sector", "date"]).reset_index(drop=True)


def load_sector_debt_structure() -> pd.DataFrame:
    """
    Annual FIBEN balance-sheet ratios by NAF sector (France, all firm sizes).

    Keeps the ratios used by the study:
      BE = share of bank debt in total financial debt (treatment definition)
      DE = financial leverage
      BF = working-capital need
    Returns a tidy frame: year, sector, ratio_code, value.
    """
    df = _read_bdf(BDF_DIR / "sector_debt_structure.csv")
    df = df[
        (df["REF_AREA"] == "FR")
        & (df["DIREN_TAILLENT"] == "TT")
        & (df["DIREN_OBJET"].isin(["BE", "DE", "BF"]))
        & (df["DIREN_SECTACT"] != "ZZ")
    ].copy()
    df["year"] = df["time_period"].astype(int)
    out = df[["year", "DIREN_SECTACT", "DIREN_OBJET", "value"]].rename(
        columns={"DIREN_SECTACT": "sector", "DIREN_OBJET": "ratio_code"}
    )
    return out.sort_values(["ratio_code", "sector", "year"]).reset_index(drop=True)


def load_ecb_rates() -> pd.DataFrame:
    """
    ECB policy rates (main refinancing and deposit facility), resampled to monthly.

    Returns a month-indexed frame with columns: main_refi, deposit_facility.
    The first hike (July 2022) is the difference-in-differences treatment date.
    """
    refi = pd.read_csv(RATES_DIR / "ecb_main_refi_rate.csv", encoding="utf-8-sig")
    depo = pd.read_csv(RATES_DIR / "ecb_deposit_facility_rate.csv", encoding="utf-8-sig")
    refi["observation_date"] = pd.to_datetime(refi["observation_date"])
    depo["observation_date"] = pd.to_datetime(depo["observation_date"])
    refi = refi.set_index("observation_date")["ECBMRRFR"].astype(float)
    depo = depo.set_index("observation_date")["ECBDFR"].astype(float)
    monthly = pd.DataFrame({
        "main_refi": refi.resample("MS").last(),
        "deposit_facility": depo.resample("MS").last(),
    })
    return monthly
