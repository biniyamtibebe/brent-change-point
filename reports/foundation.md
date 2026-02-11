# Task 1: Laying the Foundation for Analysis  
**Birhan Energies – Brent Oil Price Change Point Analysis Project**  
**Date:** February 2026  
**Prepared by:** [Your Name / Bemnet]

## 1. Data Analysis Workflow

The analysis follows this structured, reproducible workflow:

1. **Data Ingestion and Preparation**  
   - Load `BrentOilPrices.csv` using pandas.  
   - Parse `Date` column with `pd.to_datetime(errors='coerce', dayfirst=True, format='mixed')` to handle formats like `20-May-87` and `Apr 22, 2020`.  
   - Drop invalid dates, sort chronologically, remove duplicates if any.  
   - Filter to 2012–2022 for decade relevance.  
   - Create features: `log_price = np.log(Price)`, `log_returns = log_price.diff()`.

2. **Exploratory Data Analysis (EDA)**  
   - Plot raw Brent price time series.  
   - Compute and plot 365-day rolling mean for trend.  
   - Perform Augmented Dickey-Fuller (ADF) test for stationarity on raw prices and log returns.  
   - Plot log returns and 30-day rolling standard deviation to show volatility clustering.  
   - Visually annotate major spikes/drops (2014 crash, 2020 COVID collapse, 2022 Ukraine spike).

3. **Event Data Compilation**  
   - Curate 15 major events (2012–2022) from historical records, news archives, and market analyses.  
   - Store in `oil_events.csv` (Date, Event_Description, Category).  
   - Use temporal proximity (e.g., ±30 days) to associate events with detected change points.

4. **Modeling**  
   - Implement single-change-point Bayesian model in PyMC (DiscreteUniform prior on τ, Normal priors on μ₁/μ₂, HalfNormal on σ).  
   - Use `pm.math.switch` for regime-dependent mean.  
   - Sample with MCMC (2000 draws, 1000 tuning).  
   - Validate convergence (r̂ ≈ 1, trace plots).

5. **Insight Generation**  
   - Extract posterior mode/mean of τ → most likely change date.  
   - Compute % mean price shift and 95% HDI.  
   - Match change dates to events → hypothesize associations.  
   - Emphasize correlation ≠ causation discussion.

6. **Dashboard & Reporting**  
   - Flask API → serve prices, events, change points.  
   - React + Recharts frontend → interactive price chart with event markers and date filters.  
   - Final report (Medium-style) with visuals, limitations, future work.

## 2. Key Events Summary (2012–2022)

The following 15 events were selected based on documented major impacts on Brent prices (sourced from historical market reports, OPEC decisions, geopolitical timelines).

| Date       | Event Description                                                                 | Category                  |
|------------|-----------------------------------------------------------------------------------|---------------------------|
| 2012-07-01 | EU embargo on Iranian oil imports (nuclear sanctions)                             | Geopolitical / Sanctions  |
| 2014-06-01 | ISIS advances in Iraq (brief supply fear spike)                                   | Geopolitical / Conflict   |
| 2014-11-27 | OPEC refuses production cuts amid US shale boom → price collapse begins           | OPEC                      |
| 2015-07-14 | Iran nuclear deal (JCPOA) signed → sanctions relief, supply increase              | Geopolitical              |
| 2016-11-30 | OPEC agrees first cut in 8 years (1.2 mb/d) to stabilize market                   | OPEC                      |
| 2018-05-08 | US withdraws from JCPOA, re-imposes Iran sanctions → export drop                 | Geopolitical / Sanctions  |
| 2019-09-14 | Drone attacks on Saudi Aramco facilities (Abqaiq/Khurais) → ~50% output loss     | Geopolitical / Conflict   |
| 2020-03-06 | OPEC+ price war (Saudi-Russia failed cut agreement) amid early COVID demand drop  | OPEC / Economic           |
| 2020-03-11 | WHO declares COVID-19 pandemic → global lockdowns crash demand                    | Economic                  |
| 2020-04-12 | OPEC+ historic production cuts (9.7 mb/d) to counter oversupply                   | OPEC                      |
| 2021-03-23 | Ever Given blocks Suez Canal (6 days) → shipping disruption                       | Geopolitical / Logistics  |
| 2022-02-24 | Russia invades Ukraine → supply fears, sanctions → price spike >$130              | Geopolitical / Conflict   |
| 2022-03-08 | US & allies ban Russian oil imports → further supply squeeze                      | Geopolitical / Sanctions  |
| 2022-06-02 | OPEC+ accelerates production increases to ease Ukraine-war-driven high prices     | OPEC                      |
| 2022-10-05 | OPEC+ announces 2 mb/d cut amid recession fears → supports ~$100 level            | OPEC                      |

**Note:** Dates are approximate start points; market effects often lag by days/weeks.

## 3. Assumptions and Limitations

### Assumptions
- Dataset is complete and reliable (despite any truncation in sample; full file used).  
- Temporal proximity between change points and events suggests association (not causation).  
- Non-informative priors in Bayesian model for objectivity.  
- Focus on single abrupt change point (simplicity); multi-point models possible later.  
- Nominal USD prices (no inflation adjustment).

### Limitations
- **Correlation vs. Causation**: Change point detection finds structural breaks but cannot prove events caused them. Confounding factors (demand shocks, shale tech, macro conditions) possible. True causal inference needs RDD, IV, difference-in-differences, etc.  
- Daily data granularity → misses intra-day or gradual effects.  
- Single change point model → underfits periods with multiple regimes (e.g., 2020).  
- Retrospective event selection → potential confirmation bias.  
- Excludes non-geopolitical drivers (renewables growth, EV adoption, monetary policy).  
- MCMC convergence sensitive to priors and chain length.

## 4. Initial EDA Findings & Plots (to be saved from notebook)

**Data Scope (2012–2022)**  
- Date range: 2012-01-03 to 2022-11-14  
- Observations: ~2,760 trading days  
- Price statistics:  
  - Mean: ~$74.14  
  - Median: ~$67.56  
  - Min: $9.12 (Apr 2020)  
  - Max: $133.18 (Mar 2022)

**Key Plots (save as PNG from notebook)**

1. **Raw Brent Price Time Series**  
   File: `reports/figures/brent_oil_prices.png`  
   Description: Line plot showing strong volatility. Clear regimes: high ~$100+ (2012–2014), collapse 2014–2016, recovery 2017–2019, COVID crash 2020, Ukraine spike 2022.

2. **Log Returns**  
   File: `eda_log_returns.png`  
   Description: Shows volatility clustering (high variance in 2014–16, Mar 2020, Feb–Mar 2022).

3. **Rolling Volatility (30-day std of log returns)**  
   File: `reports/figures/30_Day_Rolling_Volatility.png`  
   Description: Spikes align with major events (OPEC decisions, COVID, Ukraine invasion).

**Stationarity Tests**  
- Raw prices: ADF statistic = -2.21, p-value = 0.2035 → non-stationary  
- Log returns: ADF statistic = -8.97, p-value < 0.001 → stationary  

These properties justify:  
- Log transformation / differencing  
- Regime-switching / change point approach to capture mean/volatility shifts

## Next Steps
- Run Bayesian change point model on 2012–2022 data.  
- Match detected τ to event dates.  
- Build Flask + React dashboard prototype.

**References**  
- PyMC docs: https://www.pymc.io  
- Bayesian changepoint examples: PyMC gallery  
- Historical context: EIA, OPEC MOMR, Statista, Trading Economics, IMF/ECB papers on oil & geopolitics
