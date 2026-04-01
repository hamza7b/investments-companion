import streamlit as st
import numpy as np
import pandas as pd


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r):
    st.header("Chapter 9 — Security Analysis")
    st.caption("Fundamental valuation: DuPont analysis, DDM, WACC/FCF, and comparables.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown(r"""
        **DuPont Decomposition:**
        $\text{ROE} = \underbrace{\dfrac{\text{Net Income}}{\text{Revenue}}}_{\text{Profit Margin}} \times \underbrace{\dfrac{\text{Revenue}}{\text{Total Assets}}}_{\text{Asset Turnover}} \times \underbrace{\dfrac{\text{Total Assets}}{\text{Equity}}}_{\text{Equity Multiplier}}$

        **Gordon Growth Model (DDM):**
        $V_0 = \dfrac{D_1}{k - g}$, where $g = \text{Plowback} \times \text{ROE}$

        **FCFF & Enterprise Value:**
        $\text{FCFF} = \text{EBIT}(1-\tau) + \text{Dep} - \text{CapEx} - \Delta\text{NWC}$

        $\text{WACC} = w_E k_E + w_D (1-\tau) k_D$

        $\text{Enterprise Value} = \dfrac{\text{FCFF}}{\text{WACC} - g_{FCF}}$ (Gordon growth)

        **P/E Comparables:** $V = \overline{P/E} \times \text{EPS}_\text{target}$
        """)

    # ── Section 1: DuPont Analysis ──────────────────────────────────────────
    st.subheader("DuPont Analysis")
    st.caption("Decompose ROE into three drivers: profitability, efficiency, and leverage.")

    col1, col2 = st.columns(2)
    with col1:
        net_income = st.number_input("Net Income ($M)", value=500.0, step=10.0, key="du_ni")
        revenue    = st.number_input("Revenue ($M)",    value=5000.0, step=100.0, key="du_rev")
        tot_assets = st.number_input("Total Assets ($M)", value=8000.0, step=100.0, key="du_ta")
        equity     = st.number_input("Stockholders' Equity ($M)", value=3000.0, step=100.0, key="du_eq")

    profit_margin    = net_income / revenue if revenue != 0 else 0
    asset_turnover   = revenue / tot_assets if tot_assets != 0 else 0
    equity_multiplier = tot_assets / equity if equity != 0 else 0
    roe              = profit_margin * asset_turnover * equity_multiplier

    with col2:
        c1, c2 = st.columns(2)
        c1.metric("Net Profit Margin",  f"{profit_margin*100:.2f}%")
        c1.caption("Net Income / Revenue")
        c2.metric("Asset Turnover",     f"{asset_turnover:.3f}×")
        c2.caption("Revenue / Total Assets")
        c1b, c2b = st.columns(2)
        c1b.metric("Equity Multiplier", f"{equity_multiplier:.3f}×")
        c1b.caption("Total Assets / Equity (financial leverage)")
        c2b.metric("ROE",               f"{roe*100:.2f}%")
        c2b.caption("= Margin × Turnover × Multiplier")

    st.divider()

    # ── Section 2: Gordon Growth Model (DDM) ────────────────────────────────
    st.subheader("Gordon Growth Model (DDM)")
    st.caption("Values a stock as the present value of a growing dividend stream.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Valuation inputs**")
        D1  = st.number_input("Next dividend D₁ ($)", value=2.50, step=0.10, min_value=0.01, key="ddm_D1")
        k   = st.number_input("Required return k (%)", value=8.0, step=0.1, min_value=0.1, key="ddm_k") / 100
        g   = st.number_input("Dividend growth rate g (%)", value=3.0, step=0.1, key="ddm_g") / 100

        st.markdown("**Implied g from fundamentals**")
        roe_ddm    = st.number_input("ROE (%)", value=12.0, step=0.5, key="ddm_roe") / 100
        plowback   = st.number_input("Plowback ratio (retention rate)", value=0.60, step=0.05,
                                     min_value=0.0, max_value=1.0, key="ddm_pb")
        g_implied  = roe_ddm * plowback

        st.markdown("**Reverse DDM**")
        P0_obs = st.number_input("Observed price P₀ ($)", value=50.0, step=1.0, key="ddm_P0")

    with col2:
        if k > g:
            V0 = D1 / (k - g)
            st.metric("Intrinsic Value V₀", f"${V0:.2f}")
            st.caption(f"V₀ = D₁/(k−g) = {D1:.2f}/({k*100:.1f}%−{g*100:.1f}%) = ${V0:.2f}")
            if V0 > P0_obs:
                st.success(f"V₀ (${V0:.2f}) > P₀ (${P0_obs:.2f}) → Undervalued")
            elif V0 < P0_obs:
                st.warning(f"V₀ (${V0:.2f}) < P₀ (${P0_obs:.2f}) → Overvalued")
            else:
                st.info("Fairly priced")
        else:
            st.error("k must be greater than g for the Gordon model to be valid.")
            V0 = None

        st.metric("Implied g (ROE × Plowback)", f"{g_implied*100:.2f}%")
        st.caption(f"{roe_ddm*100:.1f}% × {plowback:.2f} = {g_implied*100:.2f}%")

        if P0_obs > 0 and D1 > 0:
            k_implied = D1 / P0_obs + g
            st.metric("Implied required return k", f"{k_implied*100:.2f}%")
            st.caption(f"k = D₁/P₀ + g = {D1:.2f}/{P0_obs:.2f} + {g*100:.1f}%")

    # Sensitivity table: V0 for grid of k and g
    st.markdown("**Sensitivity Table — V₀ for different k and g**")
    k_vals = [k - 0.02, k - 0.01, k, k + 0.01, k + 0.02]
    g_vals = [g - 0.01, g, g + 0.01, g + 0.02]
    rows = {}
    for g_i in g_vals:
        row = {}
        for k_i in k_vals:
            if k_i > g_i and k_i > 0:
                row[f"k={k_i*100:.1f}%"] = f"${D1/(k_i - g_i):.2f}"
            else:
                row[f"k={k_i*100:.1f}%"] = "N/A"
        rows[f"g={g_i*100:.1f}%"] = row
    sens_df = pd.DataFrame(rows).T
    st.dataframe(sens_df, use_container_width=False)

    st.divider()

    # ── Section 3: WACC & FCF Valuation ─────────────────────────────────────
    st.subheader("WACC & Free Cash Flow Valuation")
    st.caption("Enterprise value = FCFF capitalised at WACC using a perpetual growth assumption.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**FCFF inputs**")
        ebit    = st.number_input("EBIT ($M)", value=800.0, step=10.0, key="wc_ebit")
        tau     = st.number_input("Tax rate τ (%)", value=25.0, step=1.0, key="wc_tau") / 100
        dep     = st.number_input("Depreciation ($M)", value=100.0, step=10.0, key="wc_dep")
        capex   = st.number_input("CapEx ($M)", value=150.0, step=10.0, key="wc_capex")
        d_nwc   = st.number_input("ΔNWC ($M)", value=30.0, step=5.0, key="wc_dnwc")

        st.markdown("**WACC inputs**")
        w_E    = st.number_input("Equity weight w_E", value=0.6, step=0.05, min_value=0.0, max_value=1.0, key="wc_wE")
        k_E    = st.number_input("Cost of equity k_E (%)", value=10.0, step=0.5, key="wc_kE") / 100
        k_D    = st.number_input("Cost of debt k_D (%)", value=5.0, step=0.5, key="wc_kD") / 100
        w_D    = 1 - w_E
        g_fcf  = st.number_input("FCF perpetual growth rate g (%)", value=2.0, step=0.5, key="wc_gfcf") / 100
        debt_val = st.number_input("Market value of debt ($M)", value=1000.0, step=50.0, key="wc_debt")

    fcff = ebit * (1 - tau) + dep - capex - d_nwc
    wacc = w_E * k_E + w_D * (1 - tau) * k_D

    with col2:
        st.metric("FCFF", f"${fcff:,.2f}M")
        st.caption("EBIT(1−τ) + Dep − CapEx − ΔNWC")
        st.metric("WACC", f"{wacc*100:.2f}%")
        st.caption(f"= {w_E:.1f}×{k_E*100:.1f}% + {w_D:.1f}×(1−{tau*100:.0f}%)×{k_D*100:.1f}%")
        if wacc > g_fcf:
            ev = fcff / (wacc - g_fcf)
            equity_val = ev - debt_val
            st.metric("Enterprise Value", f"${ev:,.2f}M")
            st.metric("Equity Value", f"${equity_val:,.2f}M",
                      delta=f"After subtracting ${debt_val:,.0f}M debt")
        else:
            st.error("WACC must exceed g_FCF for a finite enterprise value.")

    st.divider()

    # ── Section 4: P/E Comparables ───────────────────────────────────────────
    st.subheader("P/E Comparables Valuation")
    st.caption("Estimate target firm value using average P/E of comparable firms.")

    col1, col2 = st.columns(2)
    with col1:
        target_eps = st.number_input("Target firm EPS ($)", value=3.50, step=0.10, key="pe_eps")
        pe_input   = st.text_input("Comparable firms' P/E ratios (comma-separated)", value="18, 22, 15, 20, 19", key="pe_list")

    try:
        pe_values = [float(x.strip()) for x in pe_input.split(",") if x.strip()]
        avg_pe = np.mean(pe_values)
        implied_price = avg_pe * target_eps
        with col2:
            st.metric("Average P/E", f"{avg_pe:.2f}×")
            st.metric("Implied Stock Price", f"${implied_price:.2f}")
            st.caption(f"${target_eps:.2f} EPS × {avg_pe:.2f}× P/E = ${implied_price:.2f}")
            pe_df = pd.DataFrame({"Comparable P/E": pe_values})
            st.dataframe(pe_df, use_container_width=False, hide_index=True)
    except Exception:
        with col2:
            st.warning("Enter P/E ratios as comma-separated numbers, e.g. 18, 22, 15")
