import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src.data_utils import download_and_save_prices


@st.cache_data
def _load(ticker, start, end):
    try:
        prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
        return prices
    except Exception:
        return None


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    from src.chapter2_returns import simple_return, expected_return, volatility

    st.header("Chapter 11 — Active Portfolio Management")
    st.caption("Performance evaluation, information ratio, and the Treynor-Black model.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown(r"""
        **Performance Metrics:**
        - Sharpe ratio: $S_P = (\bar{r}_P - \bar{r}_f) / \sigma_P$
        - Jensen's alpha: $\alpha_P = \bar{r}_P - [\bar{r}_f + \beta_P(\bar{r}_M - \bar{r}_f)]$
        - Information ratio: $IR = \alpha / \sigma(e)$, where $\sigma(e)$ is idiosyncratic volatility

        **Treynor-Black Model:**
        Active assets get weight $w'_i = \alpha_i / \sigma^2(e_i)$

        Active portfolio A gets weight: $w^*_A = \dfrac{w^0_A}{1 + (1-\beta_A)w^0_A}$
        where $w^0_A = \dfrac{\alpha_A/\sigma^2(e_A)}{\mu_M/\sigma^2_M}$

        **Sharpe improvement:** $S^2_P = S^2_M + IR^2_A$
        """)

    # ── Section 1: Performance Evaluation ───────────────────────────────────
    st.subheader("Performance Evaluation")

    p_asset  = _load(ticker, start_date, end_date)
    p_market = _load(market_ticker, start_date, end_date)

    if p_asset is None or len(p_asset) < 2:
        st.error(f"Could not load data for **{ticker}**. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
        st.stop()
    if p_market is None or len(p_market) < 2:
        st.error(f"Could not load data for **{market_ticker}**. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
        st.stop()

    n = min(len(p_asset), len(p_market))
    r_asset  = simple_return(p_asset[:n])
    r_market = simple_return(p_market[:n])

    mu_a  = expected_return(r_asset)  * 252
    mu_m  = expected_return(r_market) * 252
    vol_a = volatility(r_asset)  * np.sqrt(252)
    vol_m = volatility(r_market) * np.sqrt(252)
    rf    = risk_free_rate

    cov_mat   = np.cov(r_asset, r_market, ddof=1)
    asset_beta = cov_mat[0, 1] / cov_mat[1, 1]
    alpha_j   = mu_a - (rf + asset_beta * (mu_m - rf))

    # Idiosyncratic volatility: std of residuals e_t = r_asset - (alpha_daily + beta * r_market)
    alpha_daily = expected_return(r_asset) - asset_beta * expected_return(r_market)
    residuals   = r_asset - (alpha_daily + asset_beta * r_market)
    sigma_e     = np.std(residuals, ddof=1) * np.sqrt(252)

    sharpe_a = (mu_a - rf) / vol_a if vol_a != 0 else 0.0
    sharpe_m = (mu_m - rf) / vol_m if vol_m != 0 else 0.0
    ir       = alpha_j / sigma_e if sigma_e != 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{ticker} Sharpe", f"{sharpe_a:.3f}")
    c1.caption("(μ − r_f) / σ  annualised")
    c2.metric(f"{market_ticker} Sharpe", f"{sharpe_m:.3f}")
    c2.caption("Market portfolio Sharpe ratio")
    c3.metric("Jensen's Alpha", f"{alpha_j*100:.2f}%", delta=f"{alpha_j*100:.2f}%")
    c3.caption("Excess return vs CAPM benchmark, annualised")
    c4.metric("Information Ratio", f"{ir:.3f}")
    c4.caption("α / σ(e). Measures active management skill.")

    c1b, c2b, c3b = st.columns(3)
    c1b.metric("Beta", f"{asset_beta:.4f}")
    c2b.metric("Idiosyncratic Vol σ(e)", f"{sigma_e*100:.2f}%")
    c2b.caption("Std dev of residuals from market model")
    c3b.metric("Sharpe Improvement", f"{np.sqrt(sharpe_m**2 + ir**2):.3f}")
    c3b.caption("√(S²_M + IR²) — theoretical combined Sharpe")

    st.divider()

    # Rolling 12-month Sharpe
    st.subheader("Rolling 12-Month Sharpe Ratio")
    window = 252
    if len(r_asset) > window:
        roll_sharpe_a = []
        roll_sharpe_m = []
        rf_daily = rf / 252
        for i in range(window, len(r_asset)):
            ra = r_asset[i-window:i]
            rm = r_market[i-window:i]
            s_a = (np.mean(ra) - rf_daily) / np.std(ra, ddof=1) * np.sqrt(252) if np.std(ra, ddof=1) > 0 else 0
            s_m = (np.mean(rm) - rf_daily) / np.std(rm, ddof=1) * np.sqrt(252) if np.std(rm, ddof=1) > 0 else 0
            roll_sharpe_a.append(s_a)
            roll_sharpe_m.append(s_m)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(roll_sharpe_a, color="steelblue", linewidth=1.2, label=f"{ticker}")
        ax.plot(roll_sharpe_m, color="orange", linewidth=1.2, linestyle="--", label=f"{market_ticker}")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.set_xlabel("Trading Days")
        ax.set_ylabel("Rolling Sharpe Ratio (12-month)")
        ax.set_title("Rolling 12-Month Sharpe Ratio", fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Need more than 252 days of data for a rolling Sharpe chart.")

    st.divider()

    # ── Section 2: Treynor-Black Model ───────────────────────────────────────
    st.subheader("Treynor-Black Model")
    st.caption("Optimally blend a set of active assets with the market portfolio.")

    st.markdown("Enter up to 3 active assets (analyst forecasts):")

    n_assets = st.number_input("Number of active assets", min_value=1, max_value=3, value=2, step=1, key="tb_n")
    n_assets = int(n_assets)

    asset_names, alphas, sigma_es, betas_tb = [], [], [], []
    cols = st.columns(n_assets)
    for i, col in enumerate(cols[:n_assets]):
        with col:
            st.markdown(f"**Asset {i+1}**")
            name   = st.text_input(f"Name", value=f"Stock {i+1}", key=f"tb_name_{i}")
            a_pct  = st.number_input(f"Alpha α (%)", value=2.0 if i == 0 else 1.0, step=0.1, key=f"tb_alpha_{i}")
            se_pct = st.number_input(f"Idiosyncratic σ(e) (%)", value=20.0 if i == 0 else 25.0, step=1.0, min_value=0.1, key=f"tb_se_{i}")
            b_i    = st.number_input(f"Beta β", value=1.1 if i == 0 else 0.9, step=0.05, key=f"tb_beta_{i}")
        asset_names.append(name)
        alphas.append(a_pct / 100)
        sigma_es.append(se_pct / 100)
        betas_tb.append(b_i)

    st.markdown("**Market parameters**")
    col1, col2, col3 = st.columns(3)
    mu_M_pct  = col1.number_input("Market return μ_M (%)", value=8.0, step=0.5, key="tb_muM")
    sig_M_pct = col2.number_input("Market volatility σ_M (%)", value=15.0, step=0.5, key="tb_sigM")
    rf_tb_pct = col3.number_input("Risk-free rate r_f (%)", value=risk_free_rate*100, step=0.1, key="tb_rf")

    mu_M  = mu_M_pct  / 100
    sig_M = sig_M_pct / 100
    rf_tb = rf_tb_pct / 100

    # Treynor-Black computations
    alphas = np.array(alphas)
    sigma_es = np.array(sigma_es)
    betas_tb = np.array(betas_tb)

    # Step 1: raw weights w'_i = alpha_i / sigma_e_i^2
    w_raw = alphas / (sigma_es ** 2)

    # Step 2: normalise to get active portfolio composition
    w_active = w_raw / np.sum(np.abs(w_raw))

    # Step 3: active portfolio params
    alpha_A   = np.sum(w_active * alphas)
    beta_A    = np.sum(w_active * betas_tb)
    sigma2_eA = np.sum((w_active ** 2) * (sigma_es ** 2))
    sigma_eA  = np.sqrt(sigma2_eA)

    # Step 4: initial active weight w0_A
    market_excess = mu_M - rf_tb
    if sig_M != 0 and market_excess != 0:
        w0_A = (alpha_A / sigma2_eA) / (market_excess / sig_M**2)
        # Step 5: adjusted active weight w*_A
        w_star_A = w0_A / (1 + (1 - beta_A) * w0_A)
    else:
        w0_A = 0.0
        w_star_A = 0.0

    # Sharpe improvement
    S_M  = market_excess / sig_M if sig_M != 0 else 0
    IR_A = alpha_A / sigma_eA if sigma_eA != 0 else 0
    S_P  = np.sqrt(S_M**2 + IR_A**2)

    # Display table
    tb_df = pd.DataFrame({
        "Asset": asset_names,
        "α (%)": [f"{a*100:.2f}" for a in alphas],
        "σ(e) (%)": [f"{s*100:.2f}" for s in sigma_es],
        "β": [f"{b:.3f}" for b in betas_tb],
        "w' (raw)": [f"{w:.4f}" for w in w_raw],
        "w (normalised)": [f"{w*100:.2f}%" for w in w_active],
    })
    st.dataframe(tb_df, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Active Portfolio α_A", f"{alpha_A*100:.2f}%")
    c1.metric("Active Portfolio β_A", f"{beta_A:.3f}")
    c2.metric("w*_A (optimal active weight)", f"{w_star_A*100:.2f}%")
    c2.caption("Weight in active portfolio. Remainder in market index.")
    c3.metric("Market Sharpe S_M", f"{S_M:.3f}")
    c3.metric("Total Sharpe S_P", f"{S_P:.3f}", delta=f"+{S_P-S_M:.3f} vs market")
