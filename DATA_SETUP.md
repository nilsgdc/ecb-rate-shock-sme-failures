# Data setup — download guide

Raw data is not redistributed. Download each source below and drop it into the
matching `data/raw/` subfolder. Difficulty is flagged per source: ⚡ = one-click,
🖱️ = manual selection/export on a portal, ⚠️ = needs a decision/conversion.

---

## 1. ECB policy rates ⚡ — `data/raw/bce_rates/`

One-click CSV from FRED (St. Louis Fed mirror of the official ECB series):

| Rate | Direct CSV | Save as |
|------|-----------|---------|
| Main refinancing operations | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=ECBMRRFR` | `ecb_main_refi_rate.csv` |
| Deposit facility | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=ECBDFR` | `ecb_deposit_facility_rate.csv` |

**Rupture reference:** the first hike of the cycle is **27 July 2022** — deposit
facility −0.50% → 0.00%, main refi 0.00% → 0.50%. This is the DiD treatment date
(`ECB_FIRST_HIKE = "2022-07-01"` in `src/cleaning.py`).

Official alternative (if you prefer the ECB source): ECB Data Portal →
*Key ECB interest rates* (`https://data.ecb.europa.eu/`), export CSV.

---

## 2. Business failures by sector & size 🖱️ — `data/raw/banque_de_france/`

**This is the dependent variable.** Banque de France Webstat.

- Theme page: `https://webstat.banque-france.fr/fr/themes/entreprises/defaillances-entreprises/`
- Curated selection: `https://webstat.banque-france.fr/fr/selection/5384339/`

On the portal:
1. Open the *Défaillances d'entreprises* theme.
2. Select the breakdown **by NAF sector** (A38 or A88 nomenclature) and **by firm
   size** (look for the PME / “moins de 250 salariés” dimension).
3. Set frequency = **monthly**, period from **2014** to latest (we need 2015–2019
   baseline + 2022–2023 post-treatment, plus a margin).
4. Export → **CSV** (or Excel).
5. Save as `failures_by_sector_size.csv` (or `.xlsx`).

> **Fallback if the Webstat selection is painful:** each monthly *Stat Info —
> Défaillances d'entreprises* publication on banque-france.fr ships an Excel with
> sector breakdowns. Less convenient (one file per month), but a documented backup.

---

## 3. Credit by sector (treasury vs total) 🖱️ — `data/raw/banque_de_france/`

**This builds the treatment group** (credit-intensity ratio per sector).

- Credits by firm size: `https://webstat.banque-france.fr/fr/browse.do?node=5384952`
- SME financing: `https://webstat.banque-france.fr/fr/browse.do?node=5384417`

On the portal:
1. Select **outstanding credit by NAF sector**, split into **treasury/short-term
   credit** vs **investment credit** (their sum ≈ total).
2. Frequency = **monthly**, period **2018–2021** (the window used for the ratio,
   `INTENSITY_WINDOW` in `src/cleaning.py`).
3. Export → CSV, save as `credit_by_sector.csv`.

> ⚠️ **Caveat:** the exact treasury-vs-total split at fine NAF granularity may not
> be available for every sector. If so, we adapt the treatment-construction method
> (e.g. coarser NAF level, or a proxy) and document the choice in notebook 02. Note
> what granularity you managed to export so we build the ratio accordingly.

---

## 4. ZFRR municipality list ⚠️ — `data/raw/zfrr/`

The territorial-equity classification (commune → ZFRR / ZFRR+).

- data.gouv dataset: `https://www.data.gouv.fr/datasets/zonage-france-ruralites-revitalisation-frr`
- Observatoire des Territoires (FRR): `https://www.observatoire-des-territoires.gouv.fr/frr-france-ruralites-revitalisation`

> ⚠️ The main data.gouv resource is a **shapefile** (.shp), not a flat CSV. Two options:
> - Download the shapefile — geopandas reads it directly (we already handle shapefiles
>   in the ZFE project), it contains commune INSEE codes + classification in its .dbf.
> - Or grab a plain `commune INSEE code → classification (socle / plus)` CSV from the
>   Observatoire des Territoires export if available.
>
> Save whatever you get (shapefile folder **or** CSV) in `data/raw/zfrr/` and tell me
> the format so I wire `load_zfrr_communes()` accordingly.

---

## 5. SME counts per sector ⚠️ (optional) — `data/raw/sirene/`

Used **only** to weight failure counts by the number of SMEs at risk per sector.

> ⚠️ The full SIRENE registry is ~4 GB — **overkill** for sector-level weights
> (same lesson as the ZFE project, where we filtered a 123 MB national shapefile down
> to 2.6 MB). Prefer an **INSEE aggregated table**: number of enterprises by NAF
> sector and size class (*Démographie des entreprises* / stock REE) from
> `https://www.insee.fr/`. A few hundred KB instead of gigabytes.
>
> This source is optional for a first pass — the DiD can run on failure counts alone,
> with SME-weighting added as a robustness refinement.

---

## Summary

| # | Source | Folder | Difficulty | Needed for |
|---|--------|--------|-----------|------------|
| 1 | ECB rates (FRED) | `bce_rates/` | ⚡ one-click | Treatment date |
| 2 | Failures by sector & size (Webstat) | `banque_de_france/` | 🖱️ export | Dependent variable |
| 3 | Credit by sector (Webstat) | `banque_de_france/` | 🖱️ export | Treatment group |
| 4 | ZFRR communes (data.gouv / OdT) | `zfrr/` | ⚠️ shapefile | Territorial interaction |
| 5 | SME counts (INSEE) | `sirene/` | ⚠️ optional | Weighting (robustness) |

Start with **1 → 2 → 3** (the DiD core). 4 and 5 add the equity dimension and weighting.
