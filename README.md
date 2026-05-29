# ECB Rate Shock & SME Failures — A Causal Study of French Firms

Difference-in-differences estimate of whether the 2022 ECB rate hikes accelerated
failures among French SMEs in bank-credit-dependent sectors, and whether the effect
was stronger in economically fragile regions.

---

## Research question

> Did SMEs in sectors that rely heavily on bank credit experience a statistically
> significant acceleration in failures in the 18 months following the first ECB
> rate hike (July 2022), relative to their 2015–2019 trend — and is this effect
> more pronounced in economically fragile regions?

---

## Operational definitions

The three terms in the question — *SME*, *bank-credit-dependent sector*, *fragile region* —
are defined and constructed in the study, not assumed.

### SME

Fewer than 250 employees, per the *Loi de modernisation de l'économie* of 4 August 2008
(decree n°2008-1354). This is the threshold the Banque de France and INSEE use in their
failure statistics, so it sets the granularity of the analysis.

### Bank-credit-dependent sectors

No official list exists. Each NAF sector is ranked by the **share of bank debt in total
financial debt** (bank vs bond vs leasing) — the FIBEN ratio *part des dettes bancaires* —
averaged over 2018–2021. Bank debt is the channel through which ECB rate hikes reach firms:
bank lending rates reprice, whereas bonds are fixed at issuance and leasing is contractual.
Sectors most reliant on bank debt are therefore the most exposed to monetary tightening.
Sectors above the chosen threshold form the treatment group; financial leverage
(*taux d'endettement financier*) and working-capital need (*BFR*) are used as robustness checks.

The maturity split (short-term vs long-term credit) is not available by sector in open
Banque de France data, which reports debt by instrument rather than by maturity; bank-debt
share is the available proxy for exposure to the bank-lending-rate channel.

### Economically fragile regions

Municipalities classified *Zone France Ruralités Revitalisation* (ZFRR) under the 2024
budget law (article 73, in force since 1 July 2024), which replaced the former ZRR, BER
and ZORCOMIR. Classification rests on a synthetic index of income, population and
employment over at least ten years; the lowest-index municipalities are classified ZFRR+.

---

## Method

Difference-in-differences on monthly business-failure counts by sector and firm size.

- **Treatment date:** July 2022 — the first ECB policy-rate hike.
- **Baseline:** 2015–2019.
- **Treatment group:** NAF sectors with high bank-credit dependence; **control:** low-dependence sectors.
- **Dependent variable:** monthly failures (Banque de France definition, below).
- **Territorial interaction:** ZFRR vs non-ZFRR.

---

## Separating the rate effect from the COVID/PGE rebound

State-guaranteed loans (*Prêts Garantis par l'État*, 2020–2021) suppressed failures during
the pandemic and produced a rebound in 2022–2023 that overlaps the rate effect. The analysis
separates the two by anchoring the baseline on 2015–2019 and treating 2020–2021 as an
excluded anomaly window.

---

## Definition of failure

A failure (*défaillance*) is the opening of a *redressement* or *liquidation judiciaire*
following a declaration of cessation of payments (Banque de France / INSEE). Voluntary
closures, deregistrations and disposals are excluded.

---

## Project structure

```
├── notebooks/
│   ├── 01_exploration.ipynb    # Sector debt structure, failures, ZFRR, rates
│   ├── 02_cleaning.ipynb       # Treatment-group construction, baseline, exports
│   └── 03_analysis.ipynb       # DiD, COVID/PGE handling, territorial interaction
├── src/
│   ├── data_loader.py          # Loading functions for all datasets
│   └── cleaning.py             # Cleaning and feature construction
├── data/
│   ├── raw/                    # Source files
│   └── processed/              # Cleaned exports
├── outputs/                    # Generated figures
├── requirements.txt
└── README.md
```

---

## Data sources

| Dataset | Source | Use |
|---------|--------|-----|
| Sector debt structure (bank / bond / leasing shares), annual — FIBEN balance-sheet ratios | [Banque de France — Webstat](https://webstat.banque-france.fr/) | Bank-credit-dependence ratio (treatment definition) |
| Business failures by sector and firm size, monthly | [Banque de France — Webstat](https://webstat.banque-france.fr/) | Dependent variable |
| ECB policy-rate history | [ECB](https://www.ecb.europa.eu/) / Banque de France | Treatment date (July 2022) |
| ZFRR / ZFRR+ municipality list | [data.gouv.fr](https://www.data.gouv.fr/) | Territorial classification |
| SME counts by sector | [INSEE](https://www.insee.fr/) | Weighting by SMEs at risk |
| Sectoral & price indices | [INSEE](https://www.insee.fr/) | Control variables |

---

## Limitations

1. **PGE / COVID rebound** — the main confounder; addressed by the baseline and exclusion-window design above.
2. **Treatment proxy** — open Banque de France data reports debt by instrument (bank/bond/leasing), not by maturity, so bank-credit dependence proxies exposure to the bank-lending-rate channel rather than measuring short-term credit directly.
3. **Treatment threshold** — the bank-credit-dependence cut-off is a modelling choice, tested against alternative thresholds.
4. **Aggregation** — failures are observed by sector and size class, not per firm.
5. **ZFRR timing** — the classification is in force from July 2024 and is used as a proxy for territorial fragility over 2022–2023.

---

## Stack

Python · pandas · geopandas · statsmodels · matplotlib · seaborn · Jupyter
