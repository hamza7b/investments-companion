"""
Chapter 4 — Portfolio Optimization (N-asset, up to 5 tickers).

Features:
- Asset metrics table + correlation heatmap
- 10,000-portfolio Monte Carlo cloud coloured by Sharpe ratio
- Analytical long-only efficient frontier via scipy SLSQP
- Tangency, minimum-variance, and equal-weight special portfolios
- Optimal investor portfolio via mean-variance utility maximisation
- CAL, utility curve, and weight composition bar chart
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
from src.data_utils import download_and_save_prices


@st.cache_data
def _load(ticker, start, end):
    prices, _ = download_and_save_prices(ticker, str(start), str(end), data_dir="data")
    return prices


def show(ticker, ticker2, market_ticker, start_date, end_date,
         risk_free_rate, option_T, option_r,
         ticker3="", ticker4="", ticker5=""):

    from scipy.optimize import minimize

    plt.style.use("dark_background")

    st.header("Chapter 4 — Portfolio Optimization")
    st.caption("N-asset efficient frontier, tangency portfolio, CAL, and optimal investor allocation.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown(r"""
        **Utility function:** $U = \mu_C - \tfrac{1}{2} A \sigma_C^2$
        — an investor with risk aversion $A$ maximises this over all portfolios on the CAL.

        **Capital Allocation Line (CAL):**
        $\mu_C = r_f + \sigma_C \cdot \underbrace{\dfrac{\mu_T - r_f}{\sigma_T}}_{S_T \text{ (Sharpe)}}$

        **Tangency portfolio** — the risky portfolio with the highest Sharpe ratio.
        It lies at the point where the CAL is tangent to the efficient frontier.

        **Optimal risky-asset weight:**
        $w^* = \dfrac{\mu_T - r_f}{A \cdot \sigma_T^2}$ — scales with excess return, falls with risk and risk aversion.

        **Two-fund separation:** every investor holds the same tangency portfolio $T$
        and the risk-free asset, differing only in $w^*$.

        **Efficient frontier (N assets):** the set of portfolios with minimum variance
        for each level of expected return, subject to $\sum w_i = 1$, $w_i \ge 0$ (long only).
        Traced analytically via sequential quadratic programming (SLSQP).

        **Monte Carlo cloud:** 10,000 random Dirichlet portfolios sampled from the full
        feasible set. Colour encodes Sharpe ratio — the frontier is the upper-left boundary.
        """)

    # ── 1. Collect active tickers ─────────────────────────────────────────────
    candidates = [ticker, ticker2, ticker3, ticker4, ticker5]
    tickers = [t.strip() for t in candidates if t and t.strip()]

    # ── 2. Load and align prices ──────────────────────────────────────────────
    price_series = {}
    for t in tickers:
        try:
            p = _load(t, start_date, end_date)
        except Exception:
            p = None
        if p is not None and len(p) >= 30:
            price_series[t] = p

    if len(price_series) < 2:
        st.error("Could not load data for at least 2 tickers. Try adjusting the **start or end date** in the sidebar — this usually fixes the issue after a period of inactivity.")
        st.stop()

    loaded_tickers = list(price_series.keys())
    N = len(loaded_tickers)

    # Align all series to the minimum common length
    min_len = min(len(p) for p in price_series.values())
    prices_aligned = np.column_stack([price_series[t][-min_len:] for t in loaded_tickers])  # (T+1, N)

    # Daily simple returns: (T, N)
    returns = prices_aligned[1:] / prices_aligned[:-1] - 1
    T_days = returns.shape[0]

    # Annualised statistics
    mu = returns.mean(axis=0) * 252                        # (N,)
    cov = np.cov(returns.T, ddof=1) * 252                 # (N, N)
    if N == 1:
        cov = np.array([[cov]])
    vols = np.sqrt(np.diag(cov))                          # (N,)
    sharpes = (mu - risk_free_rate) / vols                # (N,)

    # ── 3. Asset metrics table ────────────────────────────────────────────────
    st.subheader("Individual Asset Metrics")
    metrics_df = pd.DataFrame({
        "Ticker":          loaded_tickers,
        "Ann. Return (%)": [f"{m*100:.2f}" for m in mu],
        "Ann. Vol (%)":    [f"{v*100:.2f}" for v in vols],
        "Sharpe Ratio":    [f"{s:.3f}" for s in sharpes],
    })
    st.dataframe(metrics_df, use_container_width=False, hide_index=True)

    # ── 4. Correlation heatmap ────────────────────────────────────────────────
    st.subheader("Correlation Matrix")
    corr = np.corrcoef(returns.T)

    fig_corr, ax_corr = plt.subplots(figsize=(max(4, N * 1), max(2.5, N * 0.7)))
    im = ax_corr.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax_corr, fraction=0.046, pad=0.04)
    ax_corr.set_xticks(range(N)); ax_corr.set_xticklabels(loaded_tickers, fontsize=8)
    ax_corr.set_yticks(range(N)); ax_corr.set_yticklabels(loaded_tickers, fontsize=8)
    for i in range(N):
        for j in range(N):
            ax_corr.text(j, i, f"{corr[i, j]:.2f}",
                         ha="center", va="center", fontsize=7,
                         color="black" if abs(corr[i, j]) < 0.6 else "white")
    ax_corr.set_title("Asset Return Correlations", fontweight="bold", fontsize=9)
    plt.tight_layout()
    col_hm, _ = st.columns([1, 2])
    with col_hm:
        st.pyplot(fig_corr)
    plt.close(fig_corr)
    st.caption("Values close to 0 indicate low co-movement — the key driver of diversification benefit.")

    st.divider()

    # ── 5. Monte Carlo simulation ─────────────────────────────────────────────
    N_SIM = 10_000
    np.random.seed(42)
    w_sim = np.random.dirichlet(np.ones(N), size=N_SIM)           # (N_SIM, N)

    mc_ret  = w_sim @ mu                                           # (N_SIM,)
    mc_vol  = np.sqrt(np.einsum("ij,jk,ik->i", w_sim, cov, w_sim))# (N_SIM,) — vectorised
    mc_sharpe = (mc_ret - risk_free_rate) / mc_vol

    # Filter NaN/inf
    valid = np.isfinite(mc_ret) & np.isfinite(mc_vol) & np.isfinite(mc_sharpe)
    w_sim, mc_ret, mc_vol, mc_sharpe = (
        w_sim[valid], mc_ret[valid], mc_vol[valid], mc_sharpe[valid]
    )

    # ── 6. Special portfolios from Monte Carlo ────────────────────────────────
    idx_tan = np.argmax(mc_sharpe)
    idx_mvp = np.argmin(mc_vol)

    w_tan  = w_sim[idx_tan];  mu_tan  = mc_ret[idx_tan];  sig_tan  = mc_vol[idx_tan]
    w_mvp  = w_sim[idx_mvp];  mu_mvp  = mc_ret[idx_mvp];  sig_mvp  = mc_vol[idx_mvp]
    w_eq   = np.full(N, 1.0 / N)
    mu_eq  = w_eq @ mu
    sig_eq = np.sqrt(w_eq @ cov @ w_eq)

    sharpe_tan = (mu_tan - risk_free_rate) / sig_tan
    sharpe_mvp = (mu_mvp - risk_free_rate) / sig_mvp
    sharpe_eq  = (mu_eq  - risk_free_rate) / sig_eq

    # ── 7. Analytical efficient frontier (SLSQP, long-only) ──────────────────
    target_returns = np.linspace(mu.min(), mu.max(), 80)
    frontier_vol, frontier_ret = [], []

    w0 = np.full(N, 1.0 / N)
    bounds = [(0.0, 1.0)] * N
    constraints_base = [{"type": "eq", "fun": lambda w: w.sum() - 1}]

    for r_target in target_returns:
        cons = constraints_base + [
            {"type": "eq", "fun": lambda w, r=r_target: w @ mu - r}
        ]
        try:
            res = minimize(
                lambda w: w @ cov @ w,
                w0,
                method="SLSQP",
                bounds=bounds,
                constraints=cons,
                options={"ftol": 1e-10, "maxiter": 500},
            )
            if res.success:
                frontier_vol.append(np.sqrt(res.fun))
                frontier_ret.append(r_target)
        except Exception:
            pass

    frontier_vol = np.array(frontier_vol)
    frontier_ret = np.array(frontier_ret)

    # ── 8. Investor optimal portfolio ─────────────────────────────────────────
    st.subheader("Optimal Investor Portfolio")
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        A = st.slider("Risk aversion A", min_value=1.0, max_value=10.0,
                      value=3.0, step=0.5, key="ch4_A")
    with col_sl2:
        rf_override = st.number_input(
            "Risk-free rate override (%)",
            value=round(risk_free_rate * 100, 2),
            step=0.1, min_value=0.0, max_value=15.0, key="ch4_rf"
        ) / 100

    w_star = (mu_tan - rf_override) / (A * sig_tan ** 2)
    w_star = float(np.clip(w_star, 0.0, 2.0))
    mu_C   = rf_override + w_star * (mu_tan - rf_override)
    sig_C  = w_star * sig_tan
    U_C    = mu_C - 0.5 * A * sig_C ** 2

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("w* (weight in tangency)", f"{w_star*100:.1f}%")
    c1.caption("Fraction of wealth invested in the tangency portfolio; remainder in risk-free.")
    c2.metric("Optimal Return μ_C",     f"{mu_C*100:.2f}%")
    c3.metric("Optimal Volatility σ_C", f"{sig_C*100:.2f}%")
    c4.metric("Investor Utility U",     f"{U_C:.4f}")
    c4.caption("U = μ_C − ½Aσ_C². Higher A = more penalty for variance.")

    st.divider()

    # ── 9. Special portfolio weight tables ────────────────────────────────────
    st.subheader("Special Portfolio Compositions")

    def _port_df(weights, tickers):
        return pd.DataFrame({
            "Asset":      tickers,
            "Weight (%)": [f"{w*100:.2f}" for w in weights],
        })

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("**Tangency Portfolio**")
        st.dataframe(_port_df(w_tan, loaded_tickers), hide_index=True, use_container_width=True)
        st.caption(f"μ={mu_tan*100:.2f}%  σ={sig_tan*100:.2f}%  S={sharpe_tan:.3f}")
    with col_p2:
        st.markdown("**Minimum Variance Portfolio**")
        st.dataframe(_port_df(w_mvp, loaded_tickers), hide_index=True, use_container_width=True)
        st.caption(f"μ={mu_mvp*100:.2f}%  σ={sig_mvp*100:.2f}%  S={sharpe_mvp:.3f}")
    with col_p3:
        st.markdown("**Equal Weight Portfolio**")
        st.dataframe(_port_df(w_eq, loaded_tickers), hide_index=True, use_container_width=True)
        st.caption(f"μ={mu_eq*100:.2f}%  σ={sig_eq*100:.2f}%  S={sharpe_eq:.3f}")

    st.divider()

    # ── 10. Main chart — portfolio cloud ──────────────────────────────────────
    st.subheader("Efficient Frontier — Portfolio Cloud")

    # CAL: from (0, rf) through tangency, extended
    cal_vol_range = np.linspace(0, sig_tan * 1.6, 200)
    cal_ret_range = rf_override + cal_vol_range * (mu_tan - rf_override) / sig_tan

    asset_colours = plt.cm.tab10(np.linspace(0, 1, N))

    fig, ax = plt.subplots(figsize=(10, 7))

    # Monte Carlo cloud coloured by Sharpe
    sc = ax.scatter(
        mc_vol * 100, mc_ret * 100,
        c=mc_sharpe, cmap="RdYlGn",
        alpha=0.35, s=8, zorder=1,
        vmin=mc_sharpe.min(), vmax=mc_sharpe.max(),
    )
    cbar = plt.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Sharpe Ratio", fontsize=9)

    # Analytical efficient frontier
    if len(frontier_vol) > 1:
        ax.plot(frontier_vol * 100, frontier_ret * 100,
                color="white", linewidth=2.0, zorder=3, label="Efficient Frontier")

    # CAL
    ax.plot(cal_vol_range * 100, cal_ret_range * 100,
            color="#00d4aa", linewidth=1.5, linestyle="--", zorder=3, label="CAL")
    ax.scatter([0], [rf_override * 100], color="#00d4aa", s=60, zorder=4)
    ax.annotate(f"$r_f$ = {rf_override*100:.1f}%",
                xy=(0, rf_override * 100), xytext=(sig_tan * 25, rf_override * 100 + 0.3),
                color="#00d4aa", fontsize=8)

    # Tangency portfolio
    ax.scatter([sig_tan * 100], [mu_tan * 100],
               marker="*", color="gold", s=280, zorder=5,
               label=f"Tangency  S={sharpe_tan:.2f}")

    # Minimum variance portfolio
    ax.scatter([sig_mvp * 100], [mu_mvp * 100],
               marker="D", color="cyan", s=120, zorder=5,
               label=f"Min Variance  σ={sig_mvp*100:.1f}%")

    # Equal weight portfolio
    ax.scatter([sig_eq * 100], [mu_eq * 100],
               marker="o", color="magenta", s=120, zorder=5,
               label=f"Equal Weight  S={sharpe_eq:.2f}")

    # Optimal C*
    ax.scatter([sig_C * 100], [mu_C * 100],
               marker="X", color="white", s=160, zorder=5,
               label=f"C* (w*={w_star*100:.0f}% in T)  U={U_C:.3f}")

    # Individual assets
    for i, t in enumerate(loaded_tickers):
        ax.scatter([vols[i] * 100], [mu[i] * 100],
                   marker="o", color="red", s=90, zorder=6, edgecolors="white", linewidths=0.8)
        ax.annotate(t, xy=(vols[i] * 100, mu[i] * 100),
                    xytext=(4, 4), textcoords="offset points",
                    fontsize=8, color="white", fontweight="bold")

    ax.set_xlabel("Volatility (%)", fontsize=11)
    ax.set_ylabel("Expected Return (%)", fontsize=11)
    ax.set_title(f"N-Asset Efficient Frontier — {', '.join(loaded_tickers)}", fontweight="bold")
    ax.legend(fontsize=8, loc="upper left", framealpha=0.3)
    ax.grid(alpha=0.15)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.divider()

    # ── 11. Secondary charts side by side ─────────────────────────────────────
    col_u, col_bar = st.columns(2)

    # Utility curve U(w)
    with col_u:
        st.subheader("Investor Utility vs Tangency Weight")
        w_range = np.linspace(0, 2, 300)
        mu_range  = rf_override + w_range * (mu_tan - rf_override)
        sig_range = w_range * sig_tan
        U_range   = mu_range - 0.5 * A * sig_range ** 2

        fig_u, ax_u = plt.subplots(figsize=(5.5, 4))
        ax_u.plot(w_range, U_range, color="#00d4aa", linewidth=2)
        ax_u.axvline(w_star, color="orange", linestyle="--", linewidth=1.5,
                     label=f"w* = {w_star*100:.0f}%")
        ax_u.axhline(U_C, color="white", linestyle=":", linewidth=1, alpha=0.5)
        ax_u.set_xlabel("Weight in Tangency Portfolio")
        ax_u.set_ylabel("Utility U")
        ax_u.set_title("Utility Curve (A={:.1f})".format(A), fontweight="bold")
        ax_u.legend(fontsize=9)
        ax_u.grid(alpha=0.15)
        plt.tight_layout()
        st.pyplot(fig_u)
        plt.close(fig_u)
        st.caption("U peaks at w* — the optimal allocation given risk aversion A. "
                   "Leverage (w*>1) is allowed up to 2×.")

    # Weight composition bar chart
    with col_bar:
        st.subheader("Portfolio Weight Compositions")

        labels_bar = ["Tangency", "Min Var", "Equal Wt", f"C* (risky)"]
        weights_bar = [w_tan, w_mvp, w_eq, w_tan * w_star]
        # C* allocates w_star fraction of wealth to tangency, so asset weights = w_star * w_tan

        colours_bar = plt.cm.tab10(np.linspace(0, 1, N))
        fig_bar, ax_bar = plt.subplots(figsize=(5.5, 4))

        bottoms = np.zeros(4)
        for i, t in enumerate(loaded_tickers):
            vals = [weights_bar[j][i] * 100 for j in range(4)]
            ax_bar.barh(labels_bar, vals, left=bottoms,
                        color=colours_bar[i], label=t, height=0.55)
            bottoms += np.array(vals)

        ax_bar.set_xlabel("Weight (%)")
        ax_bar.set_title("Asset Allocation by Portfolio", fontweight="bold")
        ax_bar.legend(fontsize=8, loc="lower right")
        ax_bar.grid(alpha=0.15, axis="x")
        ax_bar.set_xlim(0, 105)
        plt.tight_layout()
        st.pyplot(fig_bar)
        plt.close(fig_bar)
        st.caption("C* risky weights = w* × tangency weights. "
                   f"The remaining {(1-min(w_star,1))*100:.0f}% (if any) is held in the risk-free asset.")
