import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r):
    st.header("Chapter 8 — Fixed Income Portfolios")
    st.caption("Duration, modified duration, convexity, and immunization.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
### Macaulay Duration

Macaulay duration is the weighted average time to receive the bond's cash flows, where each weight is the present value of that cash flow divided by the bond price:

$$D = \\sum_{t=1}^{T} t \\cdot w_t, \\quad w_t = \\frac{PV(CF_t)}{P}$$

---

### Modified Duration

Modified duration converts Macaulay duration into a direct measure of price sensitivity to yield changes:

$$D^* = \\frac{D}{1+r}$$

The first-order approximation for percentage price change is:

$$\\frac{\\Delta P}{P} \\approx -D^* \\cdot \\Delta r$$

---

### Convexity

Convexity captures the curvature in the price-yield relationship (the second derivative). It improves the approximation for large yield changes:

$$C = \\frac{1}{P} \\sum_{t=1}^{T} \\frac{t(t+1)\\, CF_t}{(1+r)^{t+2}}$$

The second-order price change approximation is:

$$\\frac{\\Delta P}{P} \\approx -D^* \\Delta r + \\frac{1}{2} C (\\Delta r)^2$$

Bonds with higher convexity lose less value when rates rise and gain more when rates fall — convexity is always desirable, all else equal.

---

### Special Case: Perpetuity

For a perpetuity (infinite maturity, constant coupon), modified duration simplifies to:

$$D^* = \\frac{1}{r}$$

---

### Immunization

A portfolio is immunized against interest rate risk when its duration matches the duration of the liabilities. For a two-bond portfolio:

$$w_A \\cdot D_A + (1 - w_A) \\cdot D_B = D_{\\text{target}}$$

Solving for $w_A$:

$$w_A = \\frac{D_{\\text{target}} - D_B}{D_A - D_B}$$

Immunization protects against parallel shifts in the yield curve but must be rebalanced as time passes and yields change (duration drift).
        """)

    # ── Section 1: Duration Calculator ─────────────────────────────────────
    st.subheader("Duration Calculator")

    col1, col2 = st.columns([1, 1.5])
    with col1:
        dc_F = st.number_input("Par value F ($)", value=1000.0, step=100.0, key="dc_F")
        dc_c = st.number_input("Coupon rate (%)", value=5.0, step=0.25, key="dc_c")
        dc_T = st.number_input("Maturity T (years)", value=10, step=1, min_value=1, max_value=50, key="dc_T")
        dc_r = st.number_input("YTM (%)", value=6.0, step=0.1, key="dc_r")

    r = dc_r / 100
    c = dc_c / 100
    T = int(dc_T)
    coupon = c * dc_F
    t_arr = np.arange(1, T + 1)
    cash_flows = np.full(T, coupon, dtype=float)
    cash_flows[-1] += dc_F
    pv_cf = cash_flows / (1 + r) ** t_arr
    price = np.sum(pv_cf)
    w_t = pv_cf / price
    mac_duration = np.sum(t_arr * w_t)
    mod_duration = mac_duration / (1 + r)
    # Convexity: C = [1/P] * sum_t [ t(t+1) * CF_t / (1+r)^(t+2) ]
    convexity = np.sum(t_arr * (t_arr + 1) * cash_flows / (1 + r) ** (t_arr + 2)) / price

    with col2:
        c1m, c2m, c3m = st.columns(3)
        c1m.metric("Macaulay Duration", f"{mac_duration:.4f} yrs")
        c1m.caption("Weighted average time to receive cash flows.")
        c2m.metric("Modified Duration", f"{mod_duration:.4f}")
        c2m.caption("D* = D/(1+r). Measures % price change per 1% yield change.")
        c3m.metric("Convexity", f"{convexity:.4f}")
        c3m.caption("Second-order curvature correction. Higher convexity = less price drop when rates rise.")

        st.metric("Bond Price", f"${price:,.2f}")

    # Duration weight table
    dur_df = pd.DataFrame({
        "Period t": t_arr,
        "Cash Flow CF_t": [f"${cf:.2f}" for cf in cash_flows],
        "PV(CF_t)": [f"${pv:.2f}" for pv in pv_cf],
        "Weight w_t": [f"{w:.4f}" for w in w_t],
        "t × w_t": [f"{t * w:.4f}" for t, w in zip(t_arr, w_t)],
    })
    with st.expander("Duration Weight Table", expanded=False):
        st.dataframe(dur_df, use_container_width=True, hide_index=True)
        st.caption(f"Sum of t × w_t = Macaulay Duration = {mac_duration:.4f} years")

    # Chart: duration weights bar chart
    fig0, ax0 = plt.subplots(figsize=(9, 3))
    ax0.bar(t_arr, w_t, color="steelblue", alpha=0.7, label="Weight w_t = PV(CF_t)/P")
    ax0.axvline(mac_duration, color="red", linestyle="--", linewidth=1.5,
                label=f"Macaulay Duration = {mac_duration:.2f} yrs")
    ax0.set_xlabel("Period t (years)")
    ax0.set_ylabel("Weight w_t")
    ax0.set_title("Cash Flow Weights & Macaulay Duration", fontweight="bold")
    ax0.legend(fontsize=8)
    ax0.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig0)
    plt.close(fig0)
    st.caption("The red dashed line marks the Macaulay duration — the 'centre of gravity' of the bond's cash flow timeline.")

    st.divider()

    # ── Section 2: Price Sensitivity ────────────────────────────────────────
    st.subheader("Price Sensitivity to Yield Changes")

    dr_pct = st.slider("Yield change Δr (%)", min_value=-3.0, max_value=3.0, value=1.0, step=0.1, key="ps_dr")
    dr = dr_pct / 100

    # Approximate price changes
    dp_duration_only = -mod_duration * dr * price
    dp_with_convexity = (-mod_duration * dr + 0.5 * convexity * dr ** 2) * price

    # Exact price change
    r_new = r + dr
    if r_new > 0:
        cf_new = np.full(T, coupon, dtype=float)
        cf_new[-1] += dc_F
        price_new = np.sum(cf_new / (1 + r_new) ** t_arr)
        dp_exact = price_new - price
    else:
        dp_exact = 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Duration Approx ΔP", f"${dp_duration_only:,.2f}",
                delta=f"{dp_duration_only / price * 100:.2f}%")
    col1.caption("ΔP ≈ -D* × Δr × P")
    col2.metric("Duration + Convexity ΔP", f"${dp_with_convexity:,.2f}",
                delta=f"{dp_with_convexity / price * 100:.2f}%")
    col2.caption("ΔP ≈ (-D* Δr + ½C Δr²) × P")
    col3.metric("Exact ΔP", f"${dp_exact:,.2f}",
                delta=f"{dp_exact / price * 100:.2f}%")
    col3.caption("Exact repricing. Convexity approximation is much closer to exact than duration alone.")

    # Chart: approximation quality over range of yield changes
    dr_range = np.linspace(-0.05, 0.05, 200)
    exact_changes = []
    dur_approx = []
    dur_conv_approx = []
    for dr_i in dr_range:
        r_i = r + dr_i
        if r_i > 0.0001:
            cf_i = np.full(T, coupon, dtype=float)
            cf_i[-1] += dc_F
            exact_changes.append(np.sum(cf_i / (1 + r_i) ** t_arr) - price)
        else:
            exact_changes.append(0.0)
        dur_approx.append(-mod_duration * dr_i * price)
        dur_conv_approx.append((-mod_duration * dr_i + 0.5 * convexity * dr_i ** 2) * price)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(dr_range * 100, exact_changes, color="steelblue", linewidth=2, label="Exact")
    ax.plot(dr_range * 100, dur_approx, color="red", linestyle="--", linewidth=1.5, label="Duration only")
    ax.plot(dr_range * 100, dur_conv_approx, color="orange", linestyle="--", linewidth=1.5,
            label="Duration + Convexity")
    ax.axvline(dr_pct, color="gray", linestyle=":", linewidth=1, label=f"Selected Δr = {dr_pct:.1f}%")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Yield Change Δr (%)")
    ax.set_ylabel("Price Change ΔP ($)")
    ax.set_title("Price Sensitivity: Exact vs Approximations", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Duration + convexity is a much better approximation than duration alone, especially for large yield moves.")

    st.divider()

    # ── Section 3: Duration vs Maturity & Coupon ───────────────────────────
    st.subheader("How Duration Varies with Maturity and Coupon Rate")
    st.caption("Explore how Macaulay duration changes as maturity or coupon rate changes, holding YTM fixed.")

    col1, col2 = st.columns(2)
    with col1:
        sens_F = st.number_input("Par value F ($)", value=1000.0, step=100.0, key="sens_F")
        sens_r = st.number_input("YTM for sensitivity analysis (%)", value=6.0, step=0.1, key="sens_r")

    r_sens = sens_r / 100

    # Duration vs Maturity (for several coupon rates)
    maturities_range = np.arange(1, 31)
    coupon_rates_plot = [0.02, 0.05, 0.08, 0.12]

    fig2, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(12, 4))

    for cp in coupon_rates_plot:
        durations = []
        for mat in maturities_range:
            t_i = np.arange(1, mat + 1)
            cf_i = np.full(mat, cp * sens_F, dtype=float)
            cf_i[-1] += sens_F
            pv_i = cf_i / (1 + r_sens) ** t_i
            p_i = np.sum(pv_i)
            d_i = np.sum(t_i * pv_i / p_i)
            durations.append(d_i)
        ax_left.plot(maturities_range, durations, linewidth=1.8, label=f"Coupon={cp*100:.0f}%")

    # Perpetuity duration line
    d_perp = (1 + r_sens) / r_sens
    ax_left.axhline(d_perp, color="black", linestyle=":", linewidth=1.2,
                    label=f"Perpetuity D* = 1/r = {1/r_sens:.2f}")
    ax_left.set_xlabel("Maturity (years)")
    ax_left.set_ylabel("Macaulay Duration (years)")
    ax_left.set_title("Duration vs Maturity", fontweight="bold")
    ax_left.legend(fontsize=7)
    ax_left.grid(alpha=0.3)

    # Duration vs Coupon Rate (for fixed maturity)
    coupon_range = np.linspace(0.01, 0.15, 100)
    mat_fixed_list = [5, 10, 20, 30]
    for mat_f in mat_fixed_list:
        durs_c = []
        t_f = np.arange(1, mat_f + 1)
        for cp in coupon_range:
            cf_f = np.full(mat_f, cp * sens_F, dtype=float)
            cf_f[-1] += sens_F
            pv_f = cf_f / (1 + r_sens) ** t_f
            p_f = np.sum(pv_f)
            d_f = np.sum(t_f * pv_f / p_f)
            durs_c.append(d_f)
        ax_right.plot(coupon_range * 100, durs_c, linewidth=1.8, label=f"T={mat_f}yr")

    ax_right.set_xlabel("Coupon Rate (%)")
    ax_right.set_ylabel("Macaulay Duration (years)")
    ax_right.set_title("Duration vs Coupon Rate", fontweight="bold")
    ax_right.legend(fontsize=7)
    ax_right.grid(alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)
    st.caption(
        "Left: Duration rises with maturity but is bounded by the perpetuity duration (1+r)/r. "
        "Right: Higher coupon rate pulls cash flows earlier, reducing duration."
    )

    st.divider()

    # ── Section 4: Immunization ─────────────────────────────────────────────
    st.subheader("Portfolio Immunization")
    st.caption("Immunization matches the asset portfolio duration to the liability duration, neutralizing interest rate risk.")

    st.markdown(r"""
**Immunization equation:** $w_A \cdot D_A + (1 - w_A) \cdot D_B = D_{\text{target}}$

Solving for $w_A$: $w_A = \dfrac{D_{\text{target}} - D_B}{D_A - D_B}$
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        D_target = st.slider("Target liability duration (years)", 1.0, 20.0, 7.0, 0.5, key="imm_target")
    with col2:
        D_A = st.number_input("Bond A duration (years)", value=10.0, step=0.5, min_value=0.1, key="imm_DA")
    with col3:
        D_B = st.number_input("Bond B duration (years)", value=3.0, step=0.5, min_value=0.1, key="imm_DB")

    if abs(D_A - D_B) > 1e-6:
        w_A = (D_target - D_B) / (D_A - D_B)
        w_B = 1 - w_A
        achieved_duration = w_A * D_A + w_B * D_B
        feasible = 0 <= w_A <= 1

        c1m, c2m, c3m = st.columns(3)
        c1m.metric("Weight in Bond A", f"{w_A * 100:.2f}%")
        c2m.metric("Weight in Bond B", f"{w_B * 100:.2f}%")
        c3m.metric("Achieved Duration", f"{achieved_duration:.4f} yrs")

        if not feasible:
            st.warning(
                "The target duration lies outside the range [D_B, D_A]. "
                "Immunization requires leverage (short-selling one bond). Adjust the inputs."
            )
        else:
            st.success(
                f"Immunized: {w_A * 100:.1f}% in Bond A (D={D_A}y) + "
                f"{w_B * 100:.1f}% in Bond B (D={D_B}y) → Duration = {achieved_duration:.2f}y"
            )

        # Chart: achievable duration as a function of w_A
        w_range = np.linspace(0, 1, 200)
        d_range = w_range * D_A + (1 - w_range) * D_B
        fig3, ax3 = plt.subplots(figsize=(8, 3))
        ax3.plot(w_range * 100, d_range, color="steelblue", linewidth=2, label="Portfolio Duration")
        ax3.axhline(D_target, color="orange", linestyle="--", linewidth=1.5,
                    label=f"Target Duration = {D_target:.1f} yrs")
        if feasible:
            ax3.axvline(w_A * 100, color="red", linestyle=":", linewidth=1.5,
                        label=f"w_A = {w_A * 100:.1f}%")
            ax3.scatter([w_A * 100], [achieved_duration], color="red", zorder=5, s=80)
        ax3.set_xlabel("Weight in Bond A (%)")
        ax3.set_ylabel("Portfolio Duration (years)")
        ax3.set_title("Portfolio Duration vs Weight in Bond A", fontweight="bold")
        ax3.legend(fontsize=8)
        ax3.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)
        st.caption(
            "The portfolio duration is a linear interpolation between D_B (w_A=0) and D_A (w_A=1). "
            "The target can be achieved by any combination where D_B ≤ D_target ≤ D_A."
        )

    else:
        st.warning("Bond A and Bond B have the same duration — cannot solve for weights.")

    st.divider()

    # ── Section 5: Rebalancing & Duration Drift ─────────────────────────────
    st.subheader("Duration Drift Over Time")
    st.caption(
        "Even after immunization, duration changes as time passes and yields shift. "
        "This section illustrates how a bond's modified duration drifts over its remaining life."
    )

    col1, col2 = st.columns(2)
    with col1:
        dd_F = st.number_input("Par value F ($)", value=1000.0, step=100.0, key="dd_F")
        dd_c = st.number_input("Coupon rate (%)", value=5.0, step=0.25, key="dd_c")
        dd_T = st.number_input("Original maturity T (years)", value=10, step=1, min_value=2, max_value=30, key="dd_T")
        dd_r = st.number_input("YTM (%)", value=6.0, step=0.1, key="dd_r")

    r_dd = dd_r / 100
    c_dd = dd_c / 100

    remaining_maturities = np.arange(int(dd_T), 0, -1)
    mod_dur_drift = []
    for rem in remaining_maturities:
        t_i = np.arange(1, rem + 1)
        cf_i = np.full(rem, c_dd * dd_F, dtype=float)
        cf_i[-1] += dd_F
        pv_i = cf_i / (1 + r_dd) ** t_i
        p_i = np.sum(pv_i)
        mac_i = np.sum(t_i * pv_i / p_i)
        mod_dur_drift.append(mac_i / (1 + r_dd))

    years_elapsed = int(dd_T) - remaining_maturities

    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.plot(years_elapsed, mod_dur_drift, color="steelblue", linewidth=2, label="Modified Duration")
    ax4.plot(years_elapsed, remaining_maturities - 1, color="gray", linestyle=":", linewidth=1.2,
             label="Remaining Maturity - 1 (upper bound reference)")
    ax4.set_xlabel("Years Elapsed Since Issuance")
    ax4.set_ylabel("Modified Duration (years)")
    ax4.set_title("Duration Drift Over Bond's Life", fontweight="bold")
    ax4.legend(fontsize=8)
    ax4.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)
    st.caption(
        "Modified duration declines as the bond approaches maturity, but not linearly. "
        "An immunized portfolio must be periodically rebalanced to keep asset duration aligned with liability duration."
    )
