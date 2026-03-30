import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import date

from src.chapter2_returns import simple_return, log_return, expected_return, volatility
from src.chapter3_portfolio import portfolio_return, portfolio_variance, covariance_matrix
from src.chapter5_capm import beta as estimate_beta, capm_expected_return
from src.chapter10_options import black_scholes_call, black_scholes_put
from src.data_utils import download_and_save_prices

st.set_page_config(
    page_title="Investment Companion",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def load_prices(ticker, start, end):
    try:
        prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
        return prices
    except Exception:
        return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Investment Companion")
    st.caption("Computational companion to FIN-A0104 · Aalto University")
    st.divider()

    st.subheader("Primary Asset")
    ticker = st.text_input("Ticker", value="UBS")
    start_date = st.date_input("Start date", value=date(2022, 1, 1))
    end_date = st.date_input("End date", value=date(2024, 1, 1))

    st.divider()
    st.subheader("Portfolio (Tab 2)")
    ticker2 = st.text_input("Second ticker", value="NESN.SW")

    st.divider()
    st.subheader("CAPM (Tab 3)")
    market_ticker = st.text_input("Market index", value="^SSMI")
    risk_free_rate = st.number_input("Risk-free rate (%)", value=1.5, step=0.1) / 100

    st.divider()
    st.subheader("Options (Tab 4)")
    option_T = st.number_input("Time to expiry (years)", value=0.5, step=0.1, min_value=0.01)
    option_r = st.number_input("Risk-free rate, % (options)", value=1.5, step=0.1) / 100

    st.divider()
    st.caption("Data sourced from Yahoo Finance via yfinance.")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Returns & Risk", "Portfolio", "CAPM", "Options"])


# ── Tab 1: Returns & Risk ─────────────────────────────────────────────────────
with tab1:
    st.header("Chapter 2 — Returns & Risk")
    st.caption("Simple returns, log returns, expected return, and volatility.")

    prices = load_prices(ticker, start_date, end_date)

    if prices is None or len(prices) < 2:
        st.error(f"Could not load data for **{ticker}**. Check the ticker and date range.")
        st.stop()

    ret_simple = simple_return(prices)
    ret_log = log_return(prices)

    mu_daily = expected_return(ret_simple)
    vol_daily = volatility(ret_simple)
    mu_annual = mu_daily * 252
    vol_annual = vol_daily * np.sqrt(252)
    sharpe = mu_annual / vol_annual if vol_annual != 0 else 0.0

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Return", f"{mu_annual*100:.2f}%")
    c2.metric("Annual Volatility", f"{vol_annual*100:.2f}%")
    c3.metric("Sharpe Ratio", f"{sharpe:.2f}")
    c4.metric("Trading Days", len(prices))

    st.divider()

    # Charts
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

    # Simple vs log returns comparison
    st.subheader("Simple vs Log Returns")
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


# ── Tab 2: Portfolio ──────────────────────────────────────────────────────────
with tab2:
    st.header("Chapter 3 — Two-Asset Portfolio")
    st.caption("Portfolio expected return, variance, covariance, and diversification effect.")

    p1 = load_prices(ticker, start_date, end_date)
    p2 = load_prices(ticker2, start_date, end_date)

    if p1 is None or len(p1) < 2:
        st.error(f"Could not load data for **{ticker}**.")
        st.stop()
    if p2 is None or len(p2) < 2:
        st.error(f"Could not load data for **{ticker2}**.")
        st.stop()

    # Align lengths
    n = min(len(p1), len(p2))
    r1 = simple_return(p1[:n])
    r2 = simple_return(p2[:n])

    mu1 = expected_return(r1) * 252
    mu2 = expected_return(r2) * 252
    vol1 = volatility(r1) * np.sqrt(252)
    vol2 = volatility(r2) * np.sqrt(252)

    cov_mat = covariance_matrix(np.array([r1, r2])) * 252
    corr = cov_mat[0, 1] / (vol1 * vol2)

    # Individual asset metrics
    st.subheader("Individual Asset Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{ticker} Return", f"{mu1*100:.2f}%")
    c2.metric(f"{ticker} Volatility", f"{vol1*100:.2f}%")
    c3.metric(f"{ticker2} Return", f"{mu2*100:.2f}%")
    c4.metric(f"{ticker2} Volatility", f"{vol2*100:.2f}%")
    st.metric("Correlation", f"{corr:.4f}")

    st.divider()

    # Weight slider
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
    c2.metric("Portfolio Volatility", f"{port_vol*100:.2f}%")
    c3.metric("Weighted Avg Vol", f"{weighted_avg_vol*100:.2f}%")
    c4.metric("Diversification Benefit", f"{diversification*100:.2f}%")

    st.divider()

    # Efficient frontier
    st.subheader("Efficient Frontier")
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


# ── Tab 3: CAPM ───────────────────────────────────────────────────────────────
with tab3:
    st.header("Chapter 5 — CAPM & Beta Estimation")
    st.caption("Beta estimation, market risk premium, and CAPM expected return.")

    p_asset = load_prices(ticker, start_date, end_date)
    p_market = load_prices(market_ticker, start_date, end_date)

    if p_asset is None or len(p_asset) < 2:
        st.error(f"Could not load data for **{ticker}**.")
        st.stop()
    if p_market is None or len(p_market) < 2:
        st.error(f"Could not load data for market index **{market_ticker}**.")
        st.stop()

    n = min(len(p_asset), len(p_market))
    r_asset = simple_return(p_asset[:n])
    r_market = simple_return(p_market[:n])

    asset_beta = estimate_beta(r_asset, r_market)
    market_ret = expected_return(r_market) * 252
    actual_ret = expected_return(r_asset) * 252
    capm_ret = capm_expected_return(risk_free_rate, asset_beta, market_ret)
    alpha = actual_ret - capm_ret
    market_risk_premium = market_ret - risk_free_rate

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Beta", f"{asset_beta:.4f}")
    c2.metric("CAPM Expected Return", f"{capm_ret*100:.2f}%")
    c3.metric("Actual Return", f"{actual_ret*100:.2f}%")
    c4.metric("Alpha", f"{alpha*100:.2f}%", delta=f"{alpha*100:.2f}%")

    c1, c2 = st.columns(2)
    c1.metric("Market Return", f"{market_ret*100:.2f}%")
    c2.metric("Market Risk Premium", f"{market_risk_premium*100:.2f}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # Security Market Line
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
        # Scatter with regression line
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


# ── Tab 4: Options ────────────────────────────────────────────────────────────
with tab4:
    st.header("Chapter 10 — Black-Scholes Option Pricing")
    st.caption("European call and put option pricing using the Black-Scholes model.")

    prices_opt = load_prices(ticker, start_date, end_date)

    if prices_opt is None or len(prices_opt) < 2:
        st.error(f"Could not load data for **{ticker}**.")
        st.stop()

    ret_opt = simple_return(prices_opt)
    sigma = volatility(ret_opt) * np.sqrt(252)
    S = float(prices_opt[-1])

    st.subheader("Parameters")
    col1, col2 = st.columns(2)
    with col1:
        K = st.number_input("Strike price (K)", value=round(S, 2), step=0.5)
        sigma_override = st.number_input(
            "Volatility σ (%)", value=round(sigma * 100, 2), step=0.5
        ) / 100
    with col2:
        st.metric("Current Price (S)", f"${S:.2f}")
        st.metric("Historical Volatility", f"{sigma*100:.2f}%")
        st.caption(f"T = {option_T} years  |  r = {option_r*100:.1f}%  (set in sidebar)")

    call_price = black_scholes_call(S, K, option_T, option_r, sigma_override)
    put_price = black_scholes_put(S, K, option_T, option_r, sigma_override)
    parity_lhs = call_price - put_price
    parity_rhs = S - K * np.exp(-option_r * option_T)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Call Price", f"${call_price:.4f}")
    c2.metric("Put Price", f"${put_price:.4f}")
    c3.metric("Put-Call Parity Check", f"C-P={parity_lhs:.4f}", delta=f"S-Ke^(-rT)={parity_rhs:.4f}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # Price vs underlying
        st.subheader("Price vs Stock Price")
        s_range = np.linspace(S * 0.5, S * 1.5, 200)
        calls = [black_scholes_call(s, K, option_T, option_r, sigma_override) for s in s_range]
        puts = [black_scholes_put(s, K, option_T, option_r, sigma_override) for s in s_range]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(s_range, calls, color="green", linewidth=2, label="Call")
        ax.plot(s_range, puts, color="red", linewidth=2, label="Put")
        ax.axvline(K, color="gray", linestyle="--", linewidth=1, label=f"K = {K:.2f}")
        ax.axvline(S, color="black", linestyle=":", linewidth=1, label=f"S = {S:.2f}")
        ax.set_xlabel("Stock Price ($)")
        ax.set_ylabel("Option Price ($)")
        ax.set_title("Option Price vs Underlying", fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        # Price vs volatility
        st.subheader("Price vs Volatility (Vega)")
        vol_range = np.linspace(0.05, 0.80, 200)
        calls_v = [black_scholes_call(S, K, option_T, option_r, v) for v in vol_range]
        puts_v = [black_scholes_put(S, K, option_T, option_r, v) for v in vol_range]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(vol_range * 100, calls_v, color="green", linewidth=2, label="Call")
        ax.plot(vol_range * 100, puts_v, color="red", linewidth=2, label="Put")
        ax.axvline(sigma_override * 100, color="gray", linestyle="--", linewidth=1,
                   label=f"σ = {sigma_override*100:.1f}%")
        ax.set_xlabel("Volatility (%)")
        ax.set_ylabel("Option Price ($)")
        ax.set_title("Option Price vs Volatility", fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
