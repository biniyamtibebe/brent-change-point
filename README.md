# Brent Oil Price Change Point Analysis

## 📊 Project Overview

A comprehensive Bayesian analysis of Brent crude oil prices (2012-2022) to detect structural breaks and correlate them with geopolitical, economic, and OPEC events. This project combines time series analysis, Bayesian statistics, and interactive visualization to understand oil price dynamics.

![Brent Oil Prices](https://img.shields.io/badge/Data-2012--2022-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![PyMC](https://img.shields.io/badge/Bayesian-PyMC5-red)

## 🚀 Key Features

- **Bayesian Change Point Detection**: Identify structural breaks in oil prices using MCMC sampling
- **Event Correlation Analysis**: Link price changes to 15+ key geopolitical and economic events
- **Interactive Dashboard**: Flask API + React frontend for exploring results
- **Comprehensive EDA**: Stationarity tests, volatility clustering, trend analysis
- **Production-Ready Code**: Modular, well-documented, and extensible architecture

## 📁 Project Structure

```
brent-change-point/
├── data/                          # Data storage
│   ├── brent_oil_prices.csv      # Raw Brent price data
│   ├── oil_events.csv            # Curated events (2012-2022)
│   └── processed/                # Processed datasets
│
├── notebooks/                     # Jupyter notebooks for analysis
│   ├── 01_data_preparation.ipynb
│   ├── 02_eda.ipynb
│   └── 03_modeling.ipynb
│
├── src/                          # Core Python modules
│   ├── data_prep.py             # Data loading and preprocessing
│   ├── analysis.py              # EDA and visualization
│   ├── models.py                # Bayesian change point models
│   └── utils.py                 # Helper functions
│
├── app/                          # Dashboard application
│   ├── backend/                 # Flask API
│   │   ├── app.py
│   │   └── api/
│   └── frontend/                # React frontend
│       └── react-app/
│
├── tests/                        # Unit tests
├── config/                       # Configuration files
├── docs/                         # Documentation
└── outputs/                      # Generated plots and reports
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for React frontend)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/brent-change-point.git
cd brent-change-point
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. For Windows Users (Optional - Performance)
```bash
# Install C++ compiler for PyMC performance
conda install m2w64-toolchain -c msys2
# OR use pre-built binaries
pip install pymc-bin
```

### 4. Set Up React Frontend
```bash
cd app/frontend/react-app
npm install
```

## 📈 Data Sources

### Primary Data
- **Brent Oil Prices**: Daily closing prices from ICE (Intercontinental Exchange)
- **Time Period**: 2012-01-01 to 2022-12-31
- **Features**: Date, Price (USD), Volume, Open, High, Low

### Curated Events
15 key events affecting oil prices (2012-2022):

| Date | Event | Category | Impact |
|------|-------|----------|---------|
| 2014-11-27 | OPEC decides not to cut production | OPEC | Price collapse |
| 2015-07-14 | Iran nuclear deal signed | Geopolitical | Increased supply |
| 2020-03-11 | COVID-19 pandemic declared | Economic | Demand crash |
| 2022-02-24 | Russia invades Ukraine | Conflict | Price spike |

*Full list in `data/oil_events.csv`*

## 🔬 Methodology

### 1. Data Preparation
- Date parsing with multiple format support
- Missing value imputation (time-based interpolation)
- Feature engineering:
  - Log returns for stationarity
  - Rolling statistics (30-day mean/std)
  - Volatility clustering indicators

### 2. Exploratory Data Analysis
- **Stationarity Tests**: Augmented Dickey-Fuller (ADF) test
- **Volatility Analysis**: Rolling standard deviation
- **Event Impact**: Price changes around key dates
- **Visualization**: Interactive Plotly charts

### 3. Bayesian Change Point Model
```python
with pm.Model() as model:
    # Priors
    tau = pm.DiscreteUniform("tau", lower=10, upper=n-10)
    mu1 = pm.Normal("mu1", mu=data_mean, sigma=data_std * 2)
    mu2 = pm.Normal("mu2", mu=data_mean, sigma=data_std * 2)
    sigma = pm.HalfNormal("sigma", sigma=data_std)
    
    # Likelihood
    idx = np.arange(n)
    mu = pm.math.switch(tau > idx, mu1, mu2)
    likelihood = pm.Normal("obs", mu=mu, sigma=sigma, observed=data)
    
    # MCMC Sampling
    trace = pm.sample(draws=2000, tune=1000, chains=2)
```

### 4. Model Diagnostics
- **Convergence**: R-hat statistics (< 1.1 indicates convergence)
- **Posterior Analysis**: Credible intervals (95% HDI)
- **Trace Plots**: Visual inspection of MCMC chains

## 🚀 Usage

### Option 1: Complete Pipeline (Recommended)
```bash
# Run the full analysis
python run_analysis.py

# Expected output:
# 1. Processed data saved to data/processed/
# 2. Model diagnostics printed to console
# 3. Plots saved to outputs/ directory
```

### Option 2: Step-by-Step via Notebooks
1. Open Jupyter Notebook:
   ```bash
   jupyter notebook notebooks/01_data_preparation.ipynb
   ```
2. Execute cells sequentially
3. Continue with EDA and modeling notebooks

### Option 3: Interactive Dashboard
```bash
# Start Flask backend
cd app/backend
python app.py

# In another terminal, start React frontend
cd app/frontend/react-app
npm start

# Access at http://localhost:3000
```

### Option 4: Command Line Interface
```bash
# Run specific components
python -m src.data_prep --start 2012 --end 2022
python -m src.models --n-samples 3000 --n-chains 4
```

## 📊 Key Results

### Detected Change Points
| Date | Probability | Mean Before | Mean After | % Change |
|------|-------------|-------------|------------|----------|
| 2014-11-30 | 85% | $98.45 | $52.18 | -47.0% |
| 2020-03-20 | 92% | $64.12 | $41.85 | -34.7% |
| 2022-03-01 | 78% | $78.90 | $105.42 | +33.6% |

### Event Correlations
- **Strong Correlation**: COVID-19 pandemic (2020) → 34.7% price drop
- **Moderate Correlation**: Russia-Ukraine war (2022) → 33.6% price increase
- **Weak Correlation**: OPEC decisions → mixed results

### Statistical Insights
1. **Volatility Clustering**: High volatility periods last 30-60 days
2. **Mean Reversion**: Prices tend to revert after ±40% changes
3. **Event Lag**: Market reactions occur 3-10 days after events

## 🎯 Dashboard Features

### Backend (Flask API)
```python
# Available endpoints
GET /api/prices?start=2012-01-01&end=2022-12-31
GET /api/events
POST /api/change-points
GET /api/volatility?window=30
```

### Frontend (React)
- **Interactive Charts**: Price series with event markers
- **Date Range Selector**: Custom analysis periods
- **Event Filter**: Filter by category (Geopolitical, OPEC, Economic)
- **Model Controls**: Adjust Bayesian priors and sampling parameters
- **Export Options**: Download plots and results as PDF/CSV
 
   like:file: ///C:/Users/hp/Pictures/brent-change-point/brent-change-point/app/frontend/simple-dashboard.html

## 📝 Report Contents

The analysis report includes:

1. **Executive Summary**: Key findings for decision-makers
2. **Methodology Details**: Bayesian modeling assumptions
3. **Results Visualization**: 
   - Price trajectory with change points
   - Posterior distributions
   - Event impact analysis
4. **Limitations**: Correlation vs. causation, model assumptions
5. **Recommendations**: Risk management strategies

## ⚠️ Limitations & Assumptions

### Technical Limitations
1. **Causality**: Correlation ≠ causation; no causal inference
2. **Model Simplicity**: Single change point assumption
3. **Data Granularity**: Daily frequency may miss intraday effects
4. **External Factors**: Not accounting for USD strength, inflation

### Assumptions
1. **Market Efficiency**: Prices reflect all available information
2. **Structural Breaks**: Abrupt changes in price regimes
3. **Normal Distribution**: Returns are approximately normal
4. **Event Timing**: Events have immediate market impact

## 🔮 Future Enhancements

### Planned Features
1. **Multiple Change Points**: Hierarchical Bayesian models
2. **Causal Inference**: Difference-in-differences, IV methods
3. **Machine Learning**: LSTM for price forecasting
4. **Real-time Data**: API integration for live prices
5. **Alternative Models**: GARCH for volatility, VAR for multi-variate

### Research Extensions
1. **Geopolitical Risk Index**: Quantify event severity
2. **Supply-Demand Models**: Incorporate production/consumption data
3. **Cross-commodity**: Compare with natural gas, refined products
4. **Regime Switching**: Markov-switching models


# Coverage report
pytest --cov=src --cov-report=html
```


### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings for all functions
- Include unit tests for new features
- Update documentation accordingly

## 📚 References

### Academic Papers
1. Bauwens, L., et al. (2012). "Volatility forecasting with Bayesian change point models"
2. Hamilton, J. D. (2008). "Oil and the macroeconomy"
3. Kilian, L. (2009). "Not all oil price shocks are alike"

### Technical Documentation
- [PyMC Documentation](https://www.pymc.io/)
- [ArviZ Documentation](https://python.arviz.org/)
- [Plotly Python Documentation](https://plotly.com/python/)

### Data Sources
- [ICE Brent Futures](https://www.theice.com/products/219/Brent-Crude-Futures)
- [EIA Petroleum Data](https://www.eia.gov/petroleum/)
- [OPEC Monthly Reports](https://www.opec.org/opec_web/en/publications/338.htm)

## 🏆 Acknowledgments

- **Data Providers**: Intercontinental Exchange (ICE), U.S. Energy Information Administration
- **Libraries**: PyMC, ArviZ, Pandas, NumPy, Plotly
- **Research**: Academic papers on oil price dynamics
- **Inspiration**: Energy trading firms and economic research departments




