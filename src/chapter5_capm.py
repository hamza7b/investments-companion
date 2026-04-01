import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from src.data_utils import download_and_save_prices


def beta(asset_returns, market_returns):
    """
    Estimate beta of an asset relative to the market.

    Beta measures systematic risk: how much the asset moves
    relative to the market.

    Parameters:
    -----------
    asset_returns : array-like
        Return series of the asset
    market_returns : array-like
        Return series of the market index

    Returns:
    --------
    float
        Beta: Cov(r_i, r_m) / Var(r_m)
    """
    asset_returns = np.asarray(asset_returns)
    market_returns = np.asarray(market_returns)
    cov_matrix = np.cov(asset_returns, market_returns, ddof=1)
    return cov_matrix[0, 1] / cov_matrix[1, 1]


def capm_expected_return(risk_free_rate, asset_beta, market_return):
    """
    Calculate expected return of an asset under CAPM.

    CAPM: E[r_i] = r_f + beta_i * (E[r_m] - r_f)

    Parameters:
    -----------
    risk_free_rate : float
        Risk-free rate (e.g., 0.02 for 2%)
    asset_beta : float
        Beta of the asset
    market_return : float
        Expected market return

    Returns:
    --------
    float
        CAPM expected return
    """
    market_risk_premium = market_return - risk_free_rate
    return risk_free_rate + asset_beta * market_risk_premium


@st.cache_data
def _load(ticker, start, end):
    try:
        prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
        return prices
    except Exception:
        return None


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    from src.chapter2_returns import simple_return, expected_return, volatility

    st.header("Chapter 5 — CAPM & Beta Estimation")
    st.caption("Beta estimation, market risk premium, and CAPM expected return.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        The **Capital Asset Pricing Model (CAPM)** describes the relationship between systematic risk and
        expected return for an asset:

        $E[R_i] = R_f + \\beta_i \\cdot (E[R_m] - R_f)$

        - $R_f$ — risk-free rate
        - $E[R_m] - R_f$ — **market risk premium**
        - $\\beta_i = \\dfrac{\\text{Cov}(R_i, R_m)}{\\text{Var}(R_m)}$

        **Interpretation of Beta:**
        - $\\beta = 1$: moves with market  |  $\\beta > 1$: aggressive  |  $\\beta < 1$: defensive  |  $\\beta < 0$: inverse

        **Alpha** ($\\alpha$) = actual return − CAPM predicted return. Positive = outperformed benchmark.

        The **Security Market Line (SML)** plots CAPM expected return vs beta. Points above = undervalued; below = overvalued.
        """)

    p_asset = _load(ticker, start_date, end_date)
    p_market = _load(market_ticker, start_date, end_date)

    if p_asset is None or len(p_asset) < 2:
        st.error(f"Could not load data for **{ticker}**.")
        st.stop()
    if p_market is None or len(p_market) < 2:
        st.error(f"Could not load data for market index **{market_ticker}**.")
        st.stop()

    n = min(len(p_asset), len(p_market))
    r_asset = simple_return(p_asset[:n])
    r_market = simple_return(p_market[:n])

    asset_beta = beta(r_asset, r_market)
    market_ret = expected_return(r_market) * 252
    actual_ret = expected_return(r_asset) * 252
    capm_ret = capm_expected_return(risk_free_rate, asset_beta, market_ret)
    alpha_val = actual_ret - capm_ret
    market_risk_premium = market_ret - risk_free_rate

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Beta", f"{asset_beta:.4f}")
    c1.caption("Sensitivity to market. β>1 = aggressive, β<1 = defensive.")
    c2.metric("CAPM Expected Return", f"{capm_ret*100:.2f}%")
    c2.caption("Return predicted by CAPM given the asset's beta and market risk premium.")
    c3.metric("Actual Return", f"{actual_ret*100:.2f}%")
    c3.caption("Realized annualized return over the selected period.")
    c4.metric("Alpha", f"{alpha_val*100:.2f}%", delta=f"{alpha_val*100:.2f}%")
    c4.caption("Excess return vs CAPM prediction. Positive = outperformed; negative = underperformed.")

    c1, c2 = st.columns(2)
    c1.metric("Market Return", f"{market_ret*100:.2f}%")
    c1.caption(f"Annualized return of {market_ticker} over the selected period.")
    c2.metric("Market Risk Premium", f"{market_risk_premium*100:.2f}%")
    c2.caption("Extra return the market offers above the risk-free rate.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Security Market Line")
        beta_range = np.linspace(0, 2, 200)
        sml = [capm_expected_return(risk_free_rate, b, market_ret) for b in beta_range]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(beta_range, np.array(sml) * 100, color="steelblue", linewidth=2, label="SML")
        ax.scatter([asset_beta], [capm_ret * 100], color="orange", zorder=5, s=100,
                   label=f"CAPM E[r] = {capm_ret*100:.1f}%")
        ax.scatter([asset_beta], [actual_ret * 100], color="red", zorder=5, s=100,
                   marker="D", label=f"Actual E[r] = {actual_ret*100:.1f}%")
        ax.axhline(risk_free_rate * 100, color="gray", linestyle="--", linewidth=1,
                   label=f"Risk-free = {risk_free_rate*100:.1f}%")
        ax.set_xlabel("Beta")
        ax.set_ylabel("Expected Return (%)")
        ax.set_title("Security Market Line", fontweight="bold")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.subheader(f"{ticker} vs {market_ticker}")
        intercept = expected_return(r_asset) - asset_beta * expected_return(r_market)
        x_line = np.linspace(r_market.min(), r_market.max(), 100)
        y_line = intercept + asset_beta * x_line
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(r_market * 100, r_asset * 100, alpha=0.3, s=8, color="steelblue")
        ax.plot(x_line * 100, y_line * 100, color="red", linewidth=2,
                label=f"β = {asset_beta:.3f}")
        ax.set_xlabel(f"{market_ticker} Return (%)")
        ax.set_ylabel(f"{ticker} Return (%)")
        ax.set_title("Beta Estimation (OLS)", fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
