# Computational Companion to FIN-A0104

This repository provides Python implementations of the principal quantitative models covered in *Fundamentals of Investments (FIN-A0104)* at Aalto University.

The objective is to translate theoretical finance concepts into reproducible computational workflows using Python, combining lecture formulas with market-based numerical examples.

---

# Project Scope

The repository follows the course chapter structure and focuses on models that can be directly implemented computationally.

Covered topics include:

* return measurement
* expected return estimation
* volatility analysis
* portfolio diversification
* CAPM beta estimation
* option pricing using the Black–Scholes model

All implementations are designed to remain transparent and aligned with lecture formulas rather than using high-level black-box financial libraries.

---

# Web App

The project includes an interactive Streamlit web app (`app.py`) that exposes all models through a multi-tab interface.

To launch:

```bash
streamlit run app.py
```

The app has four tabs, one per chapter, with a shared sidebar for ticker, date range, and model parameters. Each tab displays computed metrics and interactive charts driven by live or cached market data.

---

# Repository Structure

```text
investments-companion/
│── src/
│   ├── chapter2_returns.py
│   ├── chapter3_portfolio.py
│   ├── chapter5_capm.py
│   ├── chapter10_options.py
│   ├── data_utils.py
│
│── data/
│   ├── UBS_2022-01-01_2024-01-01.csv
│   ├── (additional downloaded datasets)
│
│── notebooks/
│   ├── 01_returns.ipynb
│   ├── 02_portfolio.ipynb
│   ├── 03_capm.ipynb
│   ├── 04_options.ipynb
│
│── app.py
│── requirements.txt
│── README.md
```

---

# Chapter Breakdown

## Chapter 2 — Return, Expected Return, and Volatility

Implements the core statistical measures used in investment analysis:

* simple return
* log return
* expected return
* variance
* standard deviation

Main functions:

* `simple_return()`
* `log_return()`
* `expected_return()`
* `volatility()`

This section establishes the statistical foundation required for later portfolio construction.

---

## Chapter 3 — Two-Asset Portfolio and Diversification

Implements portfolio mathematics for two risky assets.

Covered concepts:

* portfolio expected return
* portfolio variance
* covariance
* correlation
* diversification effect

Main functions:

* `portfolio_return()`
* `portfolio_variance()`
* `covariance_matrix()`

This chapter demonstrates how risk changes when combining assets.

---

## Chapter 5 — CAPM and Beta Estimation

Implements the Capital Asset Pricing Model.

Covered concepts:

* beta estimation
* market risk premium
* expected return under CAPM

Main functions:

* `beta()`
* `capm_expected_return()`

Examples use market and asset data from the SMI, UBS, and Nestlé where available.

---

## Chapter 10 — Option Pricing

Implements closed-form European option pricing.

Covered concepts:

* d1
* d2
* call option price
* put option price

Main functions:

* `black_scholes_call()`
* `black_scholes_put()`

This section applies continuous-time pricing logic using explicit formula implementation.

---

# Data Sources and Management

Market data may be retrieved using Yahoo Finance through Python interfaces such as `yfinance`.

Example assets include:

* SMI index
* UBS
* Nestlé

The purpose is to test theoretical models on real observed market prices.

## Data Management System

To avoid repeated downloads and improve workflow efficiency, the repository includes a data management utility (`src/data_utils.py`) with two functions:

### Download and Save Data

```python
from src.data_utils import download_and_save_prices

# Download data and save to CSV
prices, csv_file = download_and_save_prices(
    ticker='UBS',
    start_date='2022-01-01',
    end_date='2024-01-01',
    data_dir='data'
)
```

This saves historical prices to `data/UBS_2022-01-01_2024-01-01.csv` for reuse.

### Load from Saved Data

```python
from src.data_utils import load_prices_from_csv

# Load previously downloaded data
prices = load_prices_from_csv('data/UBS_2022-01-01_2024-01-01.csv')
```

**Benefits:**
* Speeds up notebook iterations (no repeated downloads)
* Enables reproducible analysis (same data across runs)
* Keeps data locally organized in the `data/` directory

---

# Technical Philosophy

The repository prioritizes:

* explicit formula implementation
* readability
* reproducibility
* minimal abstraction

Each model is coded directly from lecture definitions before any optimization.

---

# Educational Objective

The project serves as a computational extension of introductory investment theory.

It aims to bridge:

* lecture mathematics
* financial interpretation
* practical Python implementation

---

# Possible Extensions

Future additions may include:

* multi-asset efficient frontier
* Sharpe ratio optimization
* factor models
* Monte Carlo simulation
* bond pricing

---

# Environment

Install all required packages:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install numpy pandas matplotlib scipy yfinance streamlit
```

---

# Author Note

This repository was developed as an independent computational companion to FIN-A0104 to deepen understanding of quantitative finance concepts through implementation.
