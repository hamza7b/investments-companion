import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy.stats import norm
from src.data_utils import download_and_save_prices


def _d1(S, K, T, r, sigma):
    """
    Calculate d1 term used in the Black-Scholes formula.

    d1 = [ln(S/K) + (r + sigma^2/2) * T] / (sigma * sqrt(T))
    """
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


def _d2(S, K, T, r, sigma):
    """
    Calculate d2 term used in the Black-Scholes formula.

    d2 = d1 - sigma * sqrt(T)
    """
    return _d1(S, K, T, r, sigma) - sigma * np.sqrt(T)


def black_scholes_call(S, K, T, r, sigma):
    """
    Price a European call option using the Black-Scholes formula.

    C = S * N(d1) - K * e^(-rT) * N(d2)

    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annualized, e.g., 0.05 for 5%)
    sigma : float
        Volatility of the underlying asset (annualized, e.g., 0.20 for 20%)

    Returns:
    --------
    float
        Call option price
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def black_scholes_put(S, K, T, r, sigma):
    """
    Price a European put option using the Black-Scholes formula.

    P = K * e^(-rT) * N(-d2) - S * N(-d1)

    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annualized, e.g., 0.05 for 5%)
    sigma : float
        Volatility of the underlying asset (annualized, e.g., 0.20 for 20%)

    Returns:
    --------
    float
        Put option price
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


@st.cache_data
def _load(ticker, start, end):
    prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
    return prices


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    from src.chapter2_returns import simple_return, volatility

    st.header("Chapter 10 — Black-Scholes Option Pricing")
    st.caption("European call and put option pricing using the Black-Scholes model.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        The **Black-Scholes model** prices European options assuming the underlying stock follows
        geometric Brownian motion with constant volatility.

        **Call price:** $C = S \\cdot N(d_1) - K e^{-rT} \\cdot N(d_2)$

        **Put price:** $P = K e^{-rT} \\cdot N(-d_2) - S \\cdot N(-d_1)$

        where: $d_1 = \\dfrac{\\ln(S/K) + (r + \\sigma^2/2)T}{\\sigma\\sqrt{T}}, \\quad d_2 = d_1 - \\sigma\\sqrt{T}$

        **Put-Call Parity:** $C - P = S - K e^{-rT}$

        **Vega:** Both calls and puts increase in value when volatility rises.
        """)

    try:
        prices_opt = _load(ticker, start_date, end_date)
    except Exception:
        prices_opt = None

    if prices_opt is None or len(prices_opt) < 2:
        st.error(f"Could not load data for **{ticker}**. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
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
    c1.caption("Value of the right to buy the stock at K before expiry.")
    c2.metric("Put Price", f"${put_price:.4f}")
    c2.caption("Value of the right to sell the stock at K before expiry.")
    c3.metric("Put-Call Parity Check", f"C-P={parity_lhs:.4f}", delta=f"S-Ke^(-rT)={parity_rhs:.4f}")
    c3.caption("C − P should equal S − Ke^(−rT). A match confirms no-arbitrage consistency.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
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
        st.subheader("Price vs Volatility (Vega)")
        st.caption("Both calls and puts rise in value with higher σ — uncertainty benefits option holders.")
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
