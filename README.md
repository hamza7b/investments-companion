# Computational Companion to FIN-A0104

An interactive Streamlit web app that translates every quantitative model from *Fundamentals of Investments (FIN-A0104)* at Aalto University into live, interactive calculators driven by real market data.

🔗 **[Live App](https://investments-companion-fin-a0104.streamlit.app)**

![Investment Companion](assets/Screenshot.png)

---

## Launch

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## What It Does

Enter a ticker and date range in the sidebar. Each chapter tab renders:
- a concept overview with full formulas (LaTeX)
- live metrics computed from real Yahoo Finance data
- interactive charts and parameter sliders
- explanatory captions on every output

---

## App Structure

The app has 14 tabs, one per chapter plus a home page:

| Tab | Content |
|-----|---------|
| Home | Course map, app overview |
| Ch 1 — Intro | Markets, securities, trading glossary, margin & short-selling simulator |
| Ch 2 — Returns | Simple/log returns, expected return, volatility, Sharpe ratio |
| Ch 3 — Portfolio | Two-asset portfolio, covariance, efficient frontier |
| Ch 4 — Optimization | Tangency portfolio, CAL, optimal risky weight, utility maximisation |
| Ch 5 — CAPM | Beta estimation, SML, Jensen's alpha, market risk premium |
| Ch 6 — Empirics | Fama-French 3-factor, empirical SML, momentum effect |
| Ch 7 — Fixed Income | Bond pricing, YTM, yield curve, forward rates, zero-coupon yield |
| Ch 8 — Duration | Macaulay/modified duration, convexity, price sensitivity, immunization |
| Ch 9 — Security Analysis | DuPont, Gordon DDM, WACC/FCF valuation, P/E comparables |
| Ch 10 — Options | Black-Scholes, put-call parity, Greeks (vega) |
| Ch 11 — Active Mgmt | Performance metrics, information ratio, Treynor-Black model |
| Ch 12 — ESG | ESG pillars, screening simulator, cost of capital effects |
| Appendix A — TVM | PV/FV, annuities, perpetuities, compound growth timeline |

---

## Repository Structure

```
investments-companion/
├── app.py                      # Thin router — imports and calls each chapter's show()
├── requirements.txt
├── README.md
│
├── src/
│   ├── home.py                 # Landing page and course chapter map
│   ├── splash.py               # Full-screen splash screen on session start
│   ├── chapter1_intro.py       # Ch 1: glossary and margin/short simulator
│   ├── chapter2_returns.py     # Math: simple_return, log_return, expected_return, volatility + show()
│   ├── chapter3_portfolio.py   # Math: portfolio_return, portfolio_variance, covariance_matrix + show()
│   ├── chapter4_optimization.py# Tangency portfolio, CAL, utility optimisation
│   ├── chapter5_capm.py        # Math: beta, capm_expected_return + show()
│   ├── chapter6_empirics.py    # Fama-French, empirical SML, momentum
│   ├── chapter7_fixed_income.py# Bond pricer, YTM solver, yield curve builder
│   ├── chapter8_duration.py    # Duration, convexity, immunization
│   ├── chapter9_security.py    # DuPont, DDM, WACC/FCF, comparables
│   ├── chapter10_options.py    # Math: black_scholes_call/put + show()
│   ├── chapter11_active.py     # Performance metrics, Treynor-Black
│   ├── chapter12_esg.py        # ESG framework and screening simulator
│   ├── appendix_tvm.py         # TVM calculators and timeline visualiser
│   └── data_utils.py           # download_and_save_prices, load_prices_from_csv
│
└── data/
    └── *.csv                   # Cached price data (auto-created on first run)
```

---

## Architecture

Every chapter is a self-contained module with a `show()` function:

```python
def show(ticker, ticker2, market_ticker, start_date, end_date,
         risk_free_rate, option_T, option_r):
    ...
```

`app.py` collects sidebar inputs into a `shared` dict and calls each chapter:

```python
shared = dict(ticker=ticker, ticker2=ticker2, ...)
with tabs[2]: show_ch2(**shared)
with tabs[3]: show_ch3(**shared)
# ...
```

Chapters that use market data have a `@st.cache_data` price loader at module level. Chapters that don't (Ch 7, 8, 9, 12, Appendix A) ignore the market data parameters.

---

## Credits

- **Course:** FIN-A0104 · Fundamentals of Investments, Aalto University
- **Lecture Notes:** Prof. Petri Jylhä
- **App:** An independent computational extension — not official course material
- **Data Source:** Yahoo Finance via yfinance
- **Framework:** Streamlit

---

## Key Libraries

| Library | Use |
|---------|-----|
| `streamlit` | Web app framework |
| `numpy` | All numerical computations |
| `matplotlib` | All charts |
| `yfinance` | Market data download |
| `scipy` | YTM solver (`brentq`), option pricing (`norm.cdf`) |
| `pandas` | Data tables |

No black-box financial libraries (e.g. QuantLib, PyPortfolioOpt). Every formula is implemented directly from lecture definitions.

---

## Data

Market data is downloaded from Yahoo Finance via `yfinance` and cached locally in `data/` as CSV files. On subsequent runs the cached file is reused — no repeated downloads.

Default assets in the sidebar:
- Primary ticker: `UBS`
- Second ticker: `NESN.SW`
- Market index: `^SSMI` (SMI)

---

## Environment

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install numpy pandas matplotlib scipy yfinance streamlit
```

---

## Author Note

Developed by Hamza Bichiou, exchange student at Aalto University from EPFL (2025–2026), as an independent computational companion to FIN-A0104. Built to deepen understanding of quantitative finance through implementation.
