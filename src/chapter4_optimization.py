import streamlit as st
from src.data_utils import download_and_save_prices


@st.cache_data
def _load(ticker, start, end):
    try:
        prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
        return prices
    except Exception:
        return None


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r):
    import numpy as np
    import matplotlib.pyplot as plt
    import streamlit as st
    from src.chapter2_returns import simple_return, expected_return, volatility
    from src.chapter3_portfolio import portfolio_return, portfolio_variance, covariance_matrix

    st.header("Chapter 4 — Portfolio Optimization")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        ### Key Concepts in Portfolio Optimization

        **Utility Function**

        Investors maximise expected utility, balancing return against variance scaled by risk aversion $A$:

        $$U = \\mu_P - \\frac{1}{2} A \\sigma_P^2$$

        Higher $A$ means the investor penalises variance more heavily.

        **Capital Allocation Line (CAL)**

        The CAL describes all portfolios formed by mixing the risky portfolio $P$ with the risk-free asset $r_f$:

        $$\\mu_C = r_f + \\sigma_C \\cdot \\frac{\\mu_P - r_f}{\\sigma_P}$$

        The slope is the **Sharpe Ratio**: $S = \\dfrac{\\mu_P - r_f}{\\sigma_P}$

        **Optimal Risky Weight**

        The fraction of wealth invested in the risky portfolio that maximises utility:

        $$w^* = \\frac{\\mu_P - r_f}{A \\cdot \\sigma_P^2}$$

        **Tangency Portfolio**

        The unique risky portfolio where the CAL is tangent to the efficient frontier — i.e., the portfolio with the **maximum Sharpe ratio**.

        $$\\text{Tangency} = \\arg\\max_{w} \\frac{\\mu_P(w) - r_f}{\\sigma_P(w)}$$

        **Two-Fund Separation Theorem**

        All mean-variance efficient investors hold the same risky portfolio (the tangency portfolio), combined with the risk-free asset in proportions determined solely by their risk aversion $A$.
        """)

    # ── Load Data ────────────────────────────────────────────────────────────
    prices1 = _load(ticker, start_date, end_date)
    prices2 = _load(ticker2, start_date, end_date)

    if prices1 is None or len(prices1) < 2:
        st.error(f"Could not load data for **{ticker}**. Check the ticker and date range.")
        st.stop()
    if prices2 is None or len(prices2) < 2:
        st.error(f"Could not load data for **{ticker2}**. Check the ticker and date range.")
        st.stop()

    # Align lengths
    n = min(len(prices1), len(prices2))
    prices1 = prices1[-n:]
    prices2 = prices2[-n:]

    # Daily returns
    r1 = simple_return(prices1)
    r2 = simple_return(prices2)

    # Annualised statistics
    mu1 = expected_return(r1) * 252
    mu2 = expected_return(r2) * 252
    vol1 = volatility(r1) * np.sqrt(252)
    vol2 = volatility(r2) * np.sqrt(252)

    # Annual covariance matrix
    cov_daily = covariance_matrix(np.array([r1, r2]))
    cov_annual = cov_daily * 252
    corr = cov_annual[0, 1] / (vol1 * vol2)

    # ── Sliders ───────────────────────────────────────────────────────────────
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        A = st.slider(
            "Risk Aversion (A)",
            min_value=1.0, max_value=10.0,
            value=3.0, step=0.5,
            help="Higher A = more risk-averse investor. Drives the optimal allocation."
        )
    with col_sl2:
        rf_pct = st.slider(
            "Risk-Free Rate Override (%)",
            min_value=0.0, max_value=10.0,
            value=float(round(risk_free_rate * 100, 1)),
            step=0.1,
            help="Override the global risk-free rate for this chapter."
        )
    rf = rf_pct / 100.0

    # ── Two-Asset Efficient Frontier ──────────────────────────────────────────
    weight_range = np.linspace(0, 1, 300)

    mu_frontier = np.array([
        portfolio_return([w, 1 - w], [mu1, mu2])
        for w in weight_range
    ])
    sigma_frontier = np.array([
        np.sqrt(portfolio_variance([w, 1 - w], cov_annual))
        for w in weight_range
    ])

    # ── Tangency Portfolio ────────────────────────────────────────────────────
    sharpe_frontier = np.where(
        sigma_frontier > 1e-8,
        (mu_frontier - rf) / sigma_frontier,
        -np.inf
    )
    tangency_idx = np.argmax(sharpe_frontier)
    mu_T = mu_frontier[tangency_idx]
    sigma_T = sigma_frontier[tangency_idx]
    sharpe_T = sharpe_frontier[tangency_idx]
    w_T = weight_range[tangency_idx]        # weight in asset 1 at tangency

    # ── CAL ───────────────────────────────────────────────────────────────────
    sigma_cal = np.linspace(0, 0.5, 300)
    mu_cal = rf + sigma_cal * sharpe_T

    # ── Optimal Complete Portfolio ─────────────────────────────────────────────
    w_star_raw = (mu_T - rf) / (A * sigma_T ** 2)
    w_star = np.clip(w_star_raw, 0.0, 2.0)

    sigma_C = w_star * sigma_T
    mu_C = rf + sigma_C * sharpe_T
    utility_C = mu_C - 0.5 * A * sigma_C ** 2

    # ── Metrics Row ───────────────────────────────────────────────────────────
    st.divider()
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Tangency μ (annual)", f"{mu_T*100:.2f}%")
    m1.caption("Expected annual return of the tangency portfolio.")
    m2.metric("Tangency σ (annual)", f"{sigma_T*100:.2f}%")
    m2.caption("Annual volatility of the tangency portfolio.")
    m3.metric("Tangency Sharpe", f"{sharpe_T:.3f}")
    m3.caption("Maximum achievable Sharpe ratio on the frontier.")
    m4.metric("w* (risky weight)", f"{w_star:.3f}")
    m4.caption(f"Fraction of wealth in the tangency portfolio (A = {A}).")
    m5.metric("Utility U at C*", f"{utility_C:.4f}")
    m5.caption("Investor utility at the optimal complete portfolio C*.")

    st.divider()

    # ── Chart 1: Efficient Frontier & CAL ─────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))

    # Efficient frontier
    ax.plot(sigma_frontier * 100, mu_frontier * 100,
            color="steelblue", linewidth=2, label="Efficient Frontier")

    # CAL
    ax.plot(sigma_cal * 100, mu_cal * 100,
            color="green", linestyle="--", linewidth=1.8, label="CAL (Tangency)")

    # Tangency portfolio
    ax.scatter(sigma_T * 100, mu_T * 100,
               marker="*", s=250, color="gold", zorder=5,
               label=f"Tangency Portfolio (w₁={w_T:.2f})")

    # C* — optimal complete portfolio
    ax.scatter(sigma_C * 100, mu_C * 100,
               marker="D", s=120, color="red", zorder=5,
               label=f"C* — Optimal Complete Portfolio (w*={w_star:.2f})")

    # Individual assets
    ax.scatter(vol1 * 100, mu1 * 100,
               marker="o", s=100, color="darkorange", zorder=4,
               label=f"{ticker} (asset 1)")
    ax.scatter(vol2 * 100, mu2 * 100,
               marker="s", s=100, color="purple", zorder=4,
               label=f"{ticker2} (asset 2)")

    # Risk-free rate point
    ax.scatter(0, rf * 100,
               marker="^", s=100, color="black", zorder=4,
               label=f"Risk-Free Rate ({rf*100:.1f}%)")

    ax.set_xlabel("Annual Volatility σ (%)", fontsize=12)
    ax.set_ylabel("Annual Expected Return μ (%)", fontsize=12)
    ax.set_title("Efficient Frontier & Capital Allocation Line", fontweight="bold", fontsize=14)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        f"The **efficient frontier** (blue) traces the minimum-variance portfolios for every return level. "
        f"The **CAL** (green dashed) runs from the risk-free rate through the tangency portfolio — its slope equals "
        f"the maximum Sharpe ratio ({sharpe_T:.3f}). The **red diamond** marks C*, the optimal complete portfolio "
        f"for an investor with risk aversion A = {A}."
    )

    # ── Chart 2: Utility vs Risky Weight ─────────────────────────────────────
    st.divider()
    _, col2 = st.columns([1, 2])
    with col2:
        w_range_u = np.linspace(0, 2, 300)
        utility_curve = (rf + w_range_u * (mu_T - rf)) - 0.5 * A * (w_range_u * sigma_T) ** 2

        fig2, ax2 = plt.subplots(figsize=(7, 4))
        ax2.plot(w_range_u, utility_curve, color="steelblue", linewidth=2, label="U(w)")
        ax2.axvline(x=w_star, color="darkorange", linestyle="--", linewidth=1.8,
                    label=f"w* = {w_star:.3f}")
        ax2.scatter([w_star], [mu_C - 0.5 * A * sigma_C ** 2],
                    color="red", s=80, zorder=5)
        ax2.set_xlabel("Weight in Risky Portfolio (w)", fontsize=11)
        ax2.set_ylabel("Investor Utility U", fontsize=11)
        ax2.set_title("Investor Utility vs Risky Asset Weight",
                      fontweight="bold", fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        st.caption(
            "U peaks at w* — the optimal allocation given risk aversion A. "
            "Allocating more or less than w* lowers utility: too much weight increases variance faster "
            "than it adds return; too little leaves return on the table."
        )

    # ── Additional detail ─────────────────────────────────────────────────────
    st.divider()
    st.subheader("Input Asset Statistics")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**{ticker}**")
        st.metric("Annual μ", f"{mu1*100:.2f}%")
        st.metric("Annual σ", f"{vol1*100:.2f}%")
    with d2:
        st.markdown(f"**{ticker2}**")
        st.metric("Annual μ", f"{mu2*100:.2f}%")
        st.metric("Annual σ", f"{vol2*100:.2f}%")
    st.metric("Correlation ρ", f"{corr:.3f}")
    st.caption(
        "Correlation drives diversification benefit. A lower ρ means more risk reduction when combining assets."
    )
