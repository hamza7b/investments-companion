import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    st.header("Appendix A — Time Value of Money")
    st.caption("Present value, future value, annuities, perpetuities, and the timeline visualiser.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown(r"""
        **Present / Future Value:**
        $PV = \dfrac{FV}{(1+r)^T}$ $\qquad$ $FV = PV \cdot (1+r)^T$

        **Annuity PV:** $PV = C \cdot \dfrac{1-(1+r)^{-T}}{r}$

        **Annuity FV:** $FV = C \cdot \dfrac{(1+r)^T - 1}{r}$

        **Annuity Due:** multiply by $(1+r)$ (payments at start of period)

        **Perpetuity PV:** $PV = \dfrac{C}{r}$

        **Growing Perpetuity PV:** $PV = \dfrac{C}{r - g}$ (requires $r > g$)

        **Continuous compounding:** $PV = FV \cdot e^{-rT}$, $\quad FV = PV \cdot e^{rT}$
        """)

    # ── Section 1: PV / FV Calculator ───────────────────────────────────────
    st.subheader("Present / Future Value Calculator")

    mode = st.radio("Solve for:", ["Future Value (given PV)", "Present Value (given FV)"], horizontal=True, key="tvm_mode")
    compounding = st.radio("Compounding:", ["Discrete", "Continuous"], horizontal=True, key="tvm_comp")

    col1, col2 = st.columns(2)
    with col1:
        if mode == "Future Value (given PV)":
            pv_input = st.number_input("Present Value PV ($)", value=1000.0, step=100.0, key="tvm_pv")
        else:
            fv_input = st.number_input("Future Value FV ($)", value=1500.0, step=100.0, key="tvm_fv")
        r_tvm = st.number_input("Interest rate r (%)", value=5.0, step=0.5, min_value=0.01, key="tvm_r") / 100
        T_tvm = st.number_input("Periods T (years)", value=10, step=1, min_value=1, key="tvm_T")

    with col2:
        if mode == "Future Value (given PV)":
            if compounding == "Discrete":
                result = pv_input * (1 + r_tvm) ** T_tvm
                formula = f"FV = {pv_input:.2f} × (1 + {r_tvm*100:.1f}%)^{T_tvm}"
            else:
                result = pv_input * np.exp(r_tvm * T_tvm)
                formula = f"FV = {pv_input:.2f} × e^({r_tvm*100:.1f}% × {T_tvm})"
            st.metric("Future Value", f"${result:,.2f}")
        else:
            if compounding == "Discrete":
                result = fv_input / (1 + r_tvm) ** T_tvm
                formula = f"PV = {fv_input:.2f} / (1 + {r_tvm*100:.1f}%)^{T_tvm}"
            else:
                result = fv_input * np.exp(-r_tvm * T_tvm)
                formula = f"PV = {fv_input:.2f} × e^(−{r_tvm*100:.1f}% × {T_tvm})"
            st.metric("Present Value", f"${result:,.2f}")
        st.caption(formula)

    st.divider()

    # ── Section 2: Annuity Calculator ───────────────────────────────────────
    st.subheader("Annuity Calculator")

    col1, col2 = st.columns(2)
    with col1:
        C_ann = st.number_input("Payment C ($ per period)", value=500.0, step=50.0, key="ann_C")
        r_ann = st.number_input("Interest rate r (%)", value=6.0, step=0.5, min_value=0.01, key="ann_r") / 100
        T_ann = st.number_input("Number of periods T", value=20, step=1, min_value=1, key="ann_T")
        ann_type = st.radio("Type:", ["Ordinary Annuity (payments at end)", "Annuity Due (payments at start)"],
                            key="ann_type")

    pv_ann = C_ann * (1 - (1 + r_ann) ** (-T_ann)) / r_ann
    fv_ann = C_ann * ((1 + r_ann) ** T_ann - 1) / r_ann
    if "Due" in ann_type:
        pv_ann *= (1 + r_ann)
        fv_ann *= (1 + r_ann)

    with col2:
        st.metric("Annuity PV", f"${pv_ann:,.2f}")
        st.caption(f"PV = {C_ann:.2f} × [1−(1+{r_ann*100:.1f}%)^(−{T_ann})] / {r_ann*100:.1f}%" + (" × (1+r)" if "Due" in ann_type else ""))
        st.metric("Annuity FV", f"${fv_ann:,.2f}")
        st.caption(f"FV = {C_ann:.2f} × [(1+{r_ann*100:.1f}%)^{T_ann}−1] / {r_ann*100:.1f}%" + (" × (1+r)" if "Due" in ann_type else ""))
        total_paid = C_ann * T_ann
        interest_earned = fv_ann - total_paid
        st.metric("Total Interest Earned", f"${interest_earned:,.2f}")
        st.caption(f"FV (${fv_ann:,.2f}) − Total payments (${total_paid:,.2f})")

    st.divider()

    # ── Section 3: Perpetuity Calculator ────────────────────────────────────
    st.subheader("Perpetuity Calculator")

    col1, col2 = st.columns(2)
    with col1:
        C_perp = st.number_input("Payment C ($ per period)", value=100.0, step=10.0, key="perp_C")
        r_perp = st.number_input("Discount rate r (%)", value=5.0, step=0.5, min_value=0.01, key="perp_r") / 100
        g_perp = st.number_input("Growth rate g (%, 0 for flat perpetuity)", value=2.0, step=0.5, key="perp_g") / 100

    with col2:
        pv_flat = C_perp / r_perp
        st.metric("Flat Perpetuity PV", f"${pv_flat:,.2f}")
        st.caption(f"PV = C/r = {C_perp:.2f} / {r_perp*100:.1f}%")
        if r_perp > g_perp:
            pv_growing = C_perp / (r_perp - g_perp)
            st.metric("Growing Perpetuity PV", f"${pv_growing:,.2f}")
            st.caption(f"PV = C/(r−g) = {C_perp:.2f} / ({r_perp*100:.1f}%−{g_perp*100:.1f}%)")
        else:
            st.error("r must be greater than g for a finite growing perpetuity value.")

    st.divider()

    # ── Section 4: Timeline Visualiser ──────────────────────────────────────
    st.subheader("Wealth Growth Timeline")
    st.caption("Visualise how an initial investment compounds over time, distinguishing principal from interest.")

    col1, col2 = st.columns(2)
    with col1:
        pv_tl  = st.number_input("Initial investment ($)", value=10000.0, step=1000.0, key="tl_pv")
        r_tl   = st.number_input("Annual interest rate (%)", value=7.0, step=0.5, min_value=0.01, key="tl_r") / 100
        T_tl   = st.number_input("Number of years", value=20, step=1, min_value=1, max_value=50, key="tl_T")

    periods = np.arange(0, int(T_tl) + 1)
    balances = pv_tl * (1 + r_tl) ** periods
    interest_acc = balances - pv_tl

    with col2:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(periods, np.full(len(periods), pv_tl), color="steelblue", alpha=0.8, label="Principal")
        ax.bar(periods, interest_acc, bottom=pv_tl, color="orange", alpha=0.8, label="Accumulated Interest")
        ax.set_xlabel("Year")
        ax.set_ylabel("Wealth ($)")
        ax.set_title(f"Compound Growth: ${pv_tl:,.0f} at {r_tl*100:.1f}%", fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3, axis="y")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    final_balance = balances[-1]
    total_return = (final_balance - pv_tl) / pv_tl * 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Balance", f"${final_balance:,.2f}")
    c2.metric("Total Interest", f"${final_balance - pv_tl:,.2f}")
    c3.metric("Total Return", f"{total_return:.1f}%")
    st.caption(f"The Rule of 72: at {r_tl*100:.1f}%, wealth doubles approximately every {72/( r_tl*100):.1f} years.")
