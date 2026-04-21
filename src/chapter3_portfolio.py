import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from src.data_utils import download_and_save_prices
from src.chapter2_returns import simple_return, expected_return, volatility


def portfolio_return(weights, expected_returns):
    """
    Calculate expected return of a portfolio.

    Parameters:
    -----------
    weights : array-like
        Asset weights (must sum to 1)
    expected_returns : array-like
        Expected return of each asset

    Returns:
    --------
    float
        Portfolio expected return: sum(w_i * mu_i)
    """
    weights = np.asarray(weights)
    expected_returns = np.asarray(expected_returns)
    return np.dot(weights, expected_returns)


def portfolio_variance(weights, cov_matrix):
    """
    Calculate portfolio variance using the quadratic form w^T * Sigma * w.

    Parameters:
    -----------
    weights : array-like
        Asset weights (must sum to 1)
    cov_matrix : array-like
        Covariance matrix of asset returns (n x n)

    Returns:
    --------
    float
        Portfolio variance
    """
    weights = np.asarray(weights)
    cov_matrix = np.asarray(cov_matrix)
    return weights @ cov_matrix @ weights


def covariance_matrix(returns_matrix):
    """
    Calculate the covariance matrix from a matrix of asset returns.

    Parameters:
    -----------
    returns_matrix : array-like
        Matrix of returns with shape (n_assets, n_periods)

    Returns:
    --------
    ndarray
        Covariance matrix of shape (n_assets, n_assets)
    """
    returns_matrix = np.asarray(returns_matrix)
    return np.cov(returns_matrix, ddof=1)


@st.cache_data
def _load(ticker, start, end):
    try:
        prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
        return prices
    except Exception:
        return None


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    st.header("Chapter 3 — Two-Asset Portfolio")
    st.caption("Portfolio expected return, variance, covariance, and diversification effect.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        A **portfolio** combines multiple assets to balance risk and return. For a two-asset portfolio
        with weights $w_1$ and $w_2 = 1 - w_1$:

        **Portfolio Expected Return:**
        $\\mu_p = w_1 \\mu_1 + w_2 \\mu_2$

        **Portfolio Variance:**
        $\\sigma_p^2 = w_1^2 \\sigma_1^2 + w_2^2 \\sigma_2^2 + 2 w_1 w_2 \\sigma_{12}$

        where $\\sigma_{12} = \\rho_{12} \\cdot \\sigma_1 \\cdot \\sigma_2$ is the covariance between the two assets
        and $\\rho_{12}$ is their correlation.

        **Diversification benefit** arises when $\\rho_{12} < 1$: the portfolio volatility is lower than
        the weighted average of individual volatilities. The lower the correlation, the greater the benefit.

        The **Efficient Frontier** shows all achievable risk/return combinations. Rational investors
        choose portfolios on the upper portion (highest return for a given risk level).
        """)

    p1 = _load(ticker, start_date, end_date)
    p2 = _load(ticker2, start_date, end_date)

    if p1 is None or len(p1) < 2:
        st.error(f"Could not load data for **{ticker}**. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
        st.stop()
    if p2 is None or len(p2) < 2:
        st.error(f"Could not load data for **{ticker2}**. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
        st.stop()

    n = min(len(p1), len(p2))
    r1 = simple_return(p1[:n])
    r2 = simple_return(p2[:n])

    mu1 = expected_return(r1) * 252
    mu2 = expected_return(r2) * 252
    vol1 = volatility(r1) * np.sqrt(252)
    vol2 = volatility(r2) * np.sqrt(252)

    cov_mat = covariance_matrix(np.array([r1, r2])) * 252
    corr = cov_mat[0, 1] / (vol1 * vol2)

    st.subheader("Individual Asset Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{ticker} Return", f"{mu1*100:.2f}%")
    c2.metric(f"{ticker} Volatility", f"{vol1*100:.2f}%")
    c3.metric(f"{ticker2} Return", f"{mu2*100:.2f}%")
    c4.metric(f"{ticker2} Volatility", f"{vol2*100:.2f}%")
    st.metric("Correlation", f"{corr:.4f}")
    st.caption("Correlation ρ ranges from -1 (perfect inverse) to +1 (perfect co-movement). Values closer to 0 offer greater diversification.")

    st.divider()

    st.subheader("Portfolio Weights")
    w1 = st.slider(f"Weight in {ticker} (%)", 0, 100, 50) / 100
    w2 = 1 - w1
    st.caption(f"{ticker}: {w1*100:.0f}%  |  {ticker2}: {w2*100:.0f}%")

    weights = np.array([w1, w2])
    mu_assets = np.array([mu1, mu2])

    port_ret = portfolio_return(weights, mu_assets)
    port_var = portfolio_variance(weights, cov_mat)
    port_vol = np.sqrt(port_var)
    weighted_avg_vol = w1 * vol1 + w2 * vol2
    diversification = weighted_avg_vol - port_vol

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Return", f"{port_ret*100:.2f}%")
    c1.caption("Weighted average of individual asset returns.")
    c2.metric("Portfolio Volatility", f"{port_vol*100:.2f}%")
    c2.caption("Actual portfolio σ, accounting for correlation between assets.")
    c3.metric("Weighted Avg Vol", f"{weighted_avg_vol*100:.2f}%")
    c3.caption("What volatility would be with no diversification (ρ = 1).")
    c4.metric("Diversification Benefit", f"{diversification*100:.2f}%")
    c4.caption("Risk reduction gained by combining assets. Weighted Avg Vol − Portfolio Vol.")

    st.divider()

    st.subheader("Efficient Frontier")
    st.caption("Each point represents a portfolio with a different weight split. The curve bows left when correlation < 1, revealing the diversification gain.")
    weight_range = np.linspace(0, 1, 300)
    frontier_ret = []
    frontier_vol = []
    for w in weight_range:
        wv = np.array([w, 1 - w])
        frontier_ret.append(portfolio_return(wv, mu_assets))
        frontier_vol.append(np.sqrt(portfolio_variance(wv, cov_mat)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(np.array(frontier_vol) * 100, np.array(frontier_ret) * 100,
            color="steelblue", linewidth=2, label="Frontier")
    ax.scatter([vol1 * 100], [mu1 * 100], color="red", zorder=5, s=80, label=f"{ticker} (100%)")
    ax.scatter([vol2 * 100], [mu2 * 100], color="green", zorder=5, s=80, label=f"{ticker2} (100%)")
    ax.scatter([port_vol * 100], [port_ret * 100], color="orange", zorder=5, s=100,
               label=f"Current ({w1*100:.0f}/{w2*100:.0f})")
    ax.set_xlabel("Volatility (%)")
    ax.set_ylabel("Expected Return (%)")
    ax.set_title(f"Two-Asset Frontier: {ticker} & {ticker2}", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
