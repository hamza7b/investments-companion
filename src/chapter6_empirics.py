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

    st.header("Chapter 6 — Asset Pricing Empirics")

    # ── Concept Overview ──────────────────────────────────────────────────────
    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        ### Empirical Asset Pricing: What the Data Actually Shows

        **CAPM Prediction vs Reality**

        The CAPM predicts that only systematic risk (beta) matters, and the Security Market Line (SML) should be:

        $$E[R_i] = r_f + \\beta_i \\left(E[R_m] - r_f\\right)$$

        Empirically, the SML is **flatter** than theory predicts: low-beta stocks earn more than the CAPM says,
        and high-beta stocks earn less. A cross-sectional regression of returns on beta yields:

        $$E[R_i] = \\gamma_0 + \\gamma_1 \\beta_i$$

        where typically $\\gamma_0 > r_f$ and $\\gamma_1 < E[R_m] - r_f$.

        **Size Effect (SMB — Small Minus Big)**

        Small-capitalisation stocks have historically earned returns that exceed what their betas predict.
        Fama & French (1993) capture this with the SMB factor.

        **Value Effect (HML — High Minus Low)**

        Stocks with high book-to-market ratios (value stocks) outperform growth stocks on a risk-adjusted basis.
        The HML factor captures this premium.

        **Momentum**

        Stocks that performed well over the past 2–12 months tend to continue outperforming over the next
        few months. Jegadeesh & Titman (1993) documented this anomaly, which is not explained by the
        Fama-French three-factor model.

        **Fama-French Three-Factor Model**

        $$R_i - r_f = \\alpha + \\beta_M (R_M - r_f) + \\beta_{SMB} \\cdot SMB + \\beta_{HML} \\cdot HML + \\varepsilon$$

        Adding SMB and HML substantially improves explanatory power relative to CAPM alone.
        """)

    # ── Load Data ─────────────────────────────────────────────────────────────
    prices_asset = _load(ticker, start_date, end_date)
    prices_market = _load(market_ticker, start_date, end_date)

    if prices_asset is None or len(prices_asset) < 2:
        st.error(f"Could not load data for **{ticker}**. Check the ticker and date range.")
        st.stop()
    if prices_market is None or len(prices_market) < 2:
        st.error(f"Could not load data for **{market_ticker}**. Check the ticker and date range.")
        st.stop()

    # Align lengths and compute simple daily returns
    n = min(len(prices_asset), len(prices_market))
    prices_asset = prices_asset[-n:]
    prices_market = prices_market[-n:]

    r_asset = (prices_asset[1:] / prices_asset[:-1]) - 1
    r_market = (prices_market[1:] / prices_market[:-1]) - 1

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1 — CAPM Test
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("SECTION 1 — CAPM Empirical Test")

    # Beta via covariance
    cov_matrix = np.cov(r_asset, r_market, ddof=1)
    asset_beta = cov_matrix[0, 1] / cov_matrix[1, 1]

    # Alpha (daily OLS intercept, then annualise)
    alpha_daily = np.mean(r_asset) - asset_beta * np.mean(r_market)
    alpha_annual = alpha_daily * 252

    # Annualised returns
    actual_ret_annual = np.mean(r_asset) * 252
    market_ret_annual = np.mean(r_market) * 252
    rf = risk_free_rate

    # CAPM predicted return for this asset
    capm_predicted = rf + asset_beta * (market_ret_annual - rf)

    # Theoretical SML over beta = 0..2
    betas_sml = np.linspace(0, 2, 200)
    sml_returns = rf + betas_sml * (market_ret_annual - rf)

    # ── Metrics ───────────────────────────────────────────────────────────────
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Beta (β)", f"{asset_beta:.3f}")
    mc1.caption("Sensitivity of asset returns to market returns.")
    mc2.metric("CAPM Predicted Return", f"{capm_predicted*100:.2f}%")
    mc2.caption(f"r_f + β × (r_m − r_f) = {rf*100:.1f}% + {asset_beta:.3f} × {(market_ret_annual-rf)*100:.2f}%")
    mc3.metric("Actual Annual Return", f"{actual_ret_annual*100:.2f}%")
    mc3.caption("Realised annualised mean return over the selected period.")
    mc4.metric("Alpha (α, annualised)", f"{alpha_annual*100:.2f}%")
    mc4.caption("Return in excess of CAPM prediction. Positive α = outperformance.")

    # ── CAPM Plot ─────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))

    # Theoretical SML
    ax.plot(betas_sml, sml_returns * 100, color="steelblue", linewidth=2,
            label="Theoretical SML (CAPM)")

    # Asset: CAPM predicted return
    ax.scatter(asset_beta, capm_predicted * 100, color="darkorange", s=120,
               zorder=5, marker="o", label=f"CAPM Predicted ({capm_predicted*100:.2f}%)")

    # Asset: actual return
    ax.scatter(asset_beta, actual_ret_annual * 100, color="red", s=120,
               zorder=5, marker="D", label=f"Actual Return — {ticker} ({actual_ret_annual*100:.2f}%)")

    # Alpha arrow
    ax.annotate(
        "",
        xy=(asset_beta, actual_ret_annual * 100),
        xytext=(asset_beta, capm_predicted * 100),
        arrowprops=dict(arrowstyle="<->", color="crimson", lw=1.5)
    )
    mid_alpha = (actual_ret_annual + capm_predicted) / 2
    ax.text(asset_beta + 0.03, mid_alpha * 100,
            f"α = {alpha_annual*100:.2f}%", color="crimson", fontsize=9)

    ax.axhline(rf * 100, color="grey", linestyle=":", linewidth=1, label=f"Risk-Free Rate ({rf*100:.1f}%)")
    ax.set_xlabel("Beta (β)", fontsize=12)
    ax.set_ylabel("Annual Expected Return (%)", fontsize=12)
    ax.set_title("CAPM Empirical Test — Security Market Line", fontweight="bold", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        f"The **theoretical SML** (blue) gives the CAPM-predicted return for any beta. "
        f"The **orange dot** is where CAPM places **{ticker}** (β = {asset_beta:.3f}). "
        f"The **red diamond** is its actual realised return. "
        f"The gap is **alpha (α = {alpha_annual*100:.2f}%)** — positive means the asset earned more than "
        f"CAPM predicts. In a cross-sectional regression $E[R_i] = \\gamma_0 + \\gamma_1 \\beta_i$, "
        f"empirical work finds $\\gamma_0 > r_f$ and $\\gamma_1 < E[R_m] - r_f$, meaning the SML is "
        f"empirically flatter than theory implies."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2 — Fama-French Factor Exposures
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("SECTION 2 — Fama-French Factor Exposures")

    try:
        import yfinance as yf

        # Download factor proxies
        tickers_ff = ["IWM", "IVV", "IVE", "IVW", market_ticker]
        raw = yf.download(tickers_ff, start=str(start_date), end=str(end_date),
                          progress=False)["Close"]

        # Compute daily returns for each proxy
        ret_iwm = raw["IWM"].pct_change().dropna().values
        ret_ivv = raw["IVV"].pct_change().dropna().values
        ret_ive = raw["IVE"].pct_change().dropna().values
        ret_ivw = raw["IVW"].pct_change().dropna().values
        ret_mkt_ff = raw[market_ticker].pct_change().dropna().values

        # Align all series to minimum length
        min_len = min(len(r_asset), len(ret_iwm), len(ret_ivv),
                      len(ret_ive), len(ret_ivw), len(ret_mkt_ff))

        r_asset_ff = r_asset[-min_len:]
        ret_iwm = ret_iwm[-min_len:]
        ret_ivv = ret_ivv[-min_len:]
        ret_ive = ret_ive[-min_len:]
        ret_ivw = ret_ivw[-min_len:]
        ret_mkt_ff = ret_mkt_ff[-min_len:]

        # Factor returns
        smb = ret_iwm - ret_ivv          # small cap minus large cap
        hml = ret_ive - ret_ivw          # value minus growth

        # Excess returns
        rf_daily = risk_free_rate / 252
        r_asset_excess = r_asset_ff - rf_daily
        r_market_excess = ret_mkt_ff - rf_daily

        # OLS: [intercept, market_excess, smb, hml]
        X = np.column_stack([
            np.ones(min_len),
            r_market_excess,
            smb,
            hml
        ])
        y = r_asset_excess

        coeffs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
        alpha_ff_daily = coeffs[0]
        beta_M = coeffs[1]
        beta_SMB = coeffs[2]
        beta_HML = coeffs[3]

        alpha_ff_annual = alpha_ff_daily * 252

        # R²
        y_hat = X @ coeffs
        ss_res = np.sum((y - y_hat) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

        # Display metrics
        ff1, ff2, ff3, ff4, ff5 = st.columns(5)
        ff1.metric("β_M (Market)", f"{beta_M:.3f}")
        ff1.caption("Sensitivity to market excess return.")
        ff2.metric("β_SMB (Size)", f"{beta_SMB:.3f}")
        ff2.caption("Positive = tilts toward small-cap stocks.")
        ff3.metric("β_HML (Value)", f"{beta_HML:.3f}")
        ff3.caption("Positive = tilts toward value stocks.")
        ff4.metric("α (Fama-French, annual)", f"{alpha_ff_annual*100:.2f}%")
        ff4.caption("Unexplained return after controlling for three factors.")
        ff5.metric("R²", f"{r_squared:.3f}")
        ff5.caption("Fraction of return variance explained by the three factors.")

        st.caption(
            f"Factor proxies: **SMB** = IWM − IVV (small minus large cap); "
            f"**HML** = IVE − IVW (value minus growth). "
            f"A high R² indicates the three factors explain most of **{ticker}**'s return variation. "
            f"A positive **β_SMB** suggests the stock behaves like a small-cap; "
            f"a positive **β_HML** suggests value characteristics."
        )

    except Exception:
        st.warning(
            "Could not download Fama-French factor proxies. Check network connection."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3 — Momentum
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("SECTION 3 — Momentum")

    window = 252  # 12-month trailing window (trading days)

    if len(prices_asset) <= window:
        st.warning(
            f"Not enough data for rolling 12-month momentum. "
            f"Need at least {window + 1} price observations; got {len(prices_asset)}."
        )
    else:
        roll_ret = np.full(len(prices_asset), np.nan)
        for i in range(window, len(prices_asset)):
            roll_ret[i] = prices_asset[i] / prices_asset[i - window] - 1

        valid_idx = np.where(~np.isnan(roll_ret))[0]
        valid_ret = roll_ret[valid_idx]

        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.plot(valid_idx, valid_ret * 100, color="steelblue", linewidth=1.5,
                 label="12-Month Trailing Return")
        ax3.axhline(0, color="red", linestyle="--", linewidth=1.2, label="Zero return")
        ax3.fill_between(valid_idx, valid_ret * 100, 0,
                         where=(valid_ret >= 0), alpha=0.15, color="green", label="Positive momentum")
        ax3.fill_between(valid_idx, valid_ret * 100, 0,
                         where=(valid_ret < 0), alpha=0.15, color="red", label="Negative momentum")
        ax3.set_xlabel("Trading Day Index", fontsize=11)
        ax3.set_ylabel("12-Month Trailing Return (%)", fontsize=11)
        ax3.set_title(f"{ticker} — Rolling 12-Month Momentum",
                      fontweight="bold", fontsize=13)
        ax3.legend(fontsize=9)
        ax3.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        # Summary stats
        pos_pct = np.mean(valid_ret > 0) * 100
        mean_mom = np.mean(valid_ret) * 100
        ms1, ms2 = st.columns(2)
        ms1.metric("Mean 12-Month Return", f"{mean_mom:.2f}%")
        ms1.caption("Average trailing annual return over the sample.")
        ms2.metric("% of Months Positive", f"{pos_pct:.1f}%")
        ms2.caption("Share of rolling windows where the 12-month return was positive.")

        st.caption(
            "The **momentum effect** (Jegadeesh & Titman, 1993) documents that stocks with strong "
            "12-month trailing returns tend to continue outperforming over the next 1–6 months. "
            "Sustained positive periods (green) signal momentum; reversals (red) suggest mean-reversion. "
            "Momentum is one of the most robust and widely documented anomalies in empirical asset pricing, "
            "yet it remains difficult to explain with standard risk-based models."
        )
