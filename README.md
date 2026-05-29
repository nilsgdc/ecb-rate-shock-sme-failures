# ECB Rate Shock & SME Failures — A Causal Study of French Firms

A difference-in-differences study measuring whether the 2022 ECB rate hikes
accelerated business failures among French SMEs in credit-intensive sectors,
with a territorial-equity dimension.

> **Status:** work in progress. The framing, definitions and methodology below are
> fixed; data ingestion, cleaning and the causal analysis are being built.

---

## Research question

> Did SMEs in sectors with high short-term credit intensity experience a
> statistically significant acceleration in failures in the 18 months following
> the first ECB rate hike (July 2022), relative to their 2015–2019 historical
> trend — and is this effect more pronounced in economically fragile regions?

---

## Operational definitions

The three key terms of the question are **not** off-the-shelf categories — they are
constructed and justified inside the study. This is what separates a senior analysis
from one that assumes its premises without grounding them.

### 1. SME (PME)

- **Legal basis:** *Loi de modernisation de l'économie* (LME) of 4 August 2008,
  article 51, decree n°2008-1354 of 18 December 2008.
- **Criterion used:** fewer than 250 employees.
- **Why:** this is the nomenclature the Banque de France and INSEE use in their
  publications on business failures. Aligning the question with the granularity of
  the available data avoids rebuilding a segmentation from raw court-registry data.

### 2. Credit-intensive sectors

- There is **no official list** of these sectors — this is an analytical construction
  produced in the study (roadmap step 1, documented in the notebooks).
- **Method:** compute the ratio (short-term/treasury credit outstanding ÷ total credit
  outstanding) per NAF sector over 2018–2021, from Banque de France monthly data (Webstat).
- Sectors whose ratio exceeds a defined and justified threshold form the **treatment
  group** of the difference-in-differences design.

### 3. Economically fragile regions (ZFRR)

- **Official definition:** municipalities classified as *Zone France Ruralités
  Revitalisation* (ZFRR), introduced by the 2024 budget law (article 73), in force
  since 1 July 2024. These zones replace the former ZRR, BER and ZORCOMIR.
- **Classification criterion:** a synthetic index of income, population and employment
  dynamics over at least 10 years. The lowest-index municipalities are classified ZFRR+.
- The list of municipalities is published by decree and available as open data.

---

## Methodology

- **Design:** Difference-in-differences (DiD).
- **Rupture / treatment date:** July 2022 — the first ECB policy-rate hike.
- **Baseline:** 2015–2019 historical trend (deliberately clean of any COVID effect).
- **Treatment group:** high short-term-credit-intensity NAF sectors (constructed, see above).
- **Control group:** low-credit-intensity sectors.
- **Dependent variable:** monthly business failures (Banque de France definition, see below).
- **Territorial interaction:** ZFRR vs non-ZFRR, to test whether already-fragile areas
  paid an additional price for monetary tightening.

---

## The central methodological challenge: rate effect vs COVID/PGE rebound

State-guaranteed loans (*Prêts Garantis par l'État*, 2020–2021) artificially suppressed
business failures during the health crisis, creating a rebound effect in 2022–2023 that
**superimposes itself on the ECB-rate effect**. Disentangling the two is the real
challenge of this project, and what makes it original:

- The 2015–2019 baseline must be clean of any COVID effect.
- The 2020–2021 period must be excluded from the analysis or treated as an anomaly.
- The analysis must explicitly document this limitation and the chosen method to address
  it — which is more rigorous than ignoring it.

---

## Definition of "failure" (precise legal term)

Per the Banque de France and INSEE, a business **failure** (*défaillance*) is the opening
of a collective insolvency proceeding triggered by a declaration of cessation of payments.
It covers **only**:

- *Redressements judiciaires* (judicial reorganisation)
- *Liquidations judiciaires* (judicial liquidation)

It does **not** include voluntary closures, deregistrations, or disposals. The term is used
strictly with this definition throughout the study.

---

## Project structure

```
├── notebooks/
│   ├── 01_exploration.ipynb    # Data discovery: credit by sector, failures, ZFRR, rates
│   ├── 02_cleaning.ipynb       # Treatment-group construction, baseline, processed exports
│   └── 03_analysis.ipynb       # DiD, PGE/COVID handling, territorial interaction
├── src/
│   ├── data_loader.py          # Centralised loading functions for all datasets
│   └── cleaning.py             # Reusable cleaning pipeline
├── data/
│   ├── raw/                    # Source files (see Data sources)
│   └── processed/              # Cleaned exports
├── outputs/                    # Generated figures
├── requirements.txt
└── README.md
```

---

## Data sources

| Dataset | Source | Use |
|---------|--------|-----|
| Credit outstanding by NAF sector (treasury vs total), monthly | [Banque de France — Webstat](https://webstat.banque-france.fr/) | Build the credit-intensity ratio (treatment definition) |
| Business failures by sector and firm size, monthly | [Banque de France — Webstat](https://webstat.banque-france.fr/) | Dependent variable |
| ECB policy-rate history | [ECB](https://www.ecb.europa.eu/) / Banque de France | Temporal rupture (July 2022) |
| ZFRR / ZFRR+ municipality list | [data.gouv.fr](https://www.data.gouv.fr/) | Territorial-fragility classification |
| SIRENE business registry | [data.gouv.fr](https://www.data.gouv.fr/) / INSEE | Weight sectors by number of SMEs |
| Sectoral & price indices | [INSEE](https://www.insee.fr/) | Context and control variables |

---

## Limitations

1. **PGE / COVID rebound confounding** — the dominant threat to internal validity
   (see the dedicated section above).
2. **Treatment-group construction** — the credit-intensity threshold is a modelling
   choice; robustness to alternative thresholds will be tested.
3. **Aggregation level** — failures are observed by sector and size class, not per firm,
   which limits the controls that can be included.
4. **ZFRR timing** — the ZFRR classification is in force since July 2024; using it as a
   proxy for the fragility of territories during 2022–2023 assumes territorial fragility
   is structurally stable over the period.

---

## Stack

Python · pandas · geopandas · statsmodels · matplotlib · seaborn · Jupyter
