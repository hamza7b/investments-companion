import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from src.data_utils import download_and_save_prices


def simple_return(prices):
    """
    Calculate simple returns from a price series.

    Parameters:
    -----------
    prices : array-like
        Price series (1D array or list)

    Returns:
    --------
    returns : ndarray
        Simple returns: (P_t - P_{t-1}) / P_{t-1}
    """
    prices = np.asarray(prices)
    return (prices[1:] / prices[:-1]) - 1

# Alternative return measyure: log returns,
# which are often used in finance for their properties (e.g., time-additivity).
def log_return(prices):
    """
    Calculate log returns from a price series.

    Parameters:
    -----------
    prices : array-like
        Price series (1D array or list)

    Returns:
    --------
    returns : ndarray
        Log returns: ln(P_t / P_{t-1})
    """
    prices = np.asarray(prices)
    return np.log(prices[1:] / prices[:-1])


def expected_return(returns):
    """
    Calculate expected return (mean return).

    Parameters:
    -----------
    returns : array-like
        Series of returns

    Returns:
    --------
    expected_return : float
        Mean return
    """
    return np.mean(returns)


def volatility(returns):
    """
    Calculate volatility (standard deviation of returns).

    Parameters:
    -----------
    returns : array-like
        Series of returns

    Returns:
    --------
    volatility : float
        Standard deviation of returns
    """
    return np.std(returns, ddof=1)


@st.cache_data
def _load(ticker, start, end):
    try:
        prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
        return prices
    except Exception:
        return None


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    st.header("Chapter 2 — Returns & Risk")
    st.caption("Simple returns, log returns, expected return, and volatility.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        **Returns** measure how much an investment gains or loses over a period.
        There are two common ways to compute them:

        - **Simple return:** $R_t = \\dfrac{P_t - P_{t-1}}{P_{t-1}}$
        - **Log return:** $r_t = \\ln\\left(\\dfrac{P_t}{P_{t-1}}\\right)$

        Log returns are preferred in many financial models because they are time-additive and
        approximately normally distributed for small values.

        **Expected return** is the arithmetic mean of past returns, used as a proxy for future performance:
        $\\mu = \\dfrac{1}{T} \\sum_{t=1}^{T} R_t$

        **Volatility** (standard deviation of returns) measures risk — how much returns deviate from their mean:
        $\\sigma = \\sqrt{\\dfrac{1}{T-1} \\sum_{t=1}^{T} (R_t - \\mu)^2}$

        Daily values are **annualized** by multiplying $\\mu$ by 252 and $\\sigma$ by $\\sqrt{252}$ (trading days per year).

        The **Sharpe Ratio** measures return per unit of risk: $S = \\dfrac{\\mu_{annual}}{\\sigma_{annual}}$
        """)

    prices = _load(ticker, start_date, end_date)

    if prices is None or len(prices) < 2:
        st.error(f"Could not load data for **{ticker}**. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
        st.stop()

    ret_simple = simple_return(prices)
    ret_log = log_return(prices)

    mu_daily = expected_return(ret_simple)
    vol_daily = volatility(ret_simple)
    mu_annual = mu_daily * 252
    vol_annual = vol_daily * np.sqrt(252)
    sharpe = mu_annual / vol_annual if vol_annual != 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Return", f"{mu_annual*100:.2f}%")
    c1.caption("Mean daily return × 252 trading days.")
    c2.metric("Annual Volatility", f"{vol_annual*100:.2f}%")
    c2.caption("Daily σ scaled by √252. Higher = more risk.")
    c3.metric("Sharpe Ratio", f"{sharpe:.2f}")
    c3.caption("Return per unit of risk (annual μ / annual σ). >1 is generally considered good.")
    c4.metric("Trading Days", len(prices))
    c4.caption("Number of price observations in the selected period.")

    st.divider()

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.5))
    axes[0].plot(prices, linewidth=1.5, color="steelblue")
    axes[0].set_title(f"{ticker} Price Series", fontweight="bold")
    axes[0].set_ylabel("Price ($)")
    axes[0].grid(alpha=0.3)
    colors = ["green" if r > 0 else "red" for r in ret_simple]
    axes[1].bar(range(len(ret_simple)), ret_simple * 100, color=colors, alpha=0.7, width=1)
    axes[1].axhline(0, color="black", linewidth=0.5)
    axes[1].set_title("Daily Simple Returns", fontweight="bold")
    axes[1].set_ylabel("Return (%)")
    axes[1].grid(alpha=0.3)
    axes[2].hist(ret_simple * 100, bins=40, color="skyblue", edgecolor="black", alpha=0.7)
    axes[2].set_title("Return Distribution", fontweight="bold")
    axes[2].set_xlabel("Return (%)")
    axes[2].set_ylabel("Frequency")
    axes[2].grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.divider()
    st.subheader("Simple vs Log Returns")
    st.caption("For small returns, simple and log returns are nearly identical. Log returns diverge slightly for larger moves.")
    col1, col2 = st.columns(2)
    with col1:
        fig2, ax = plt.subplots(figsize=(6, 3))
        ax.plot(ret_simple * 100, label="Simple", alpha=0.7, linewidth=0.8)
        ax.plot(ret_log * 100, label="Log", alpha=0.7, linewidth=0.8, linestyle="--")
        ax.set_title("Daily Returns Comparison", fontweight="bold")
        ax.set_ylabel("Return (%)")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    with col2:
        fig3, ax = plt.subplots(figsize=(6, 3))
        ax.scatter(ret_simple * 100, ret_log * 100, alpha=0.3, s=8, color="steelblue")
        ax.set_xlabel("Simple Return (%)")
        ax.set_ylabel("Log Return (%)")
        ax.set_title("Simple vs Log (scatter)", fontweight="bold")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)
