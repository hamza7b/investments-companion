import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import brentq


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r, **kwargs):
    st.header("Chapter 7 — Fixed Income Securities")
    st.caption("Bond pricing, yield to maturity, the term structure, and forward rates.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
### Bond Pricing

A coupon bond pays periodic coupons $c \\cdot F$ and par $F$ at maturity. Its price is the present value of all cash flows:

$$P = \\sum_{t=1}^{T} \\frac{c \\cdot F}{(1+r)^t} + \\frac{F}{(1+r)^T}$$

where $c$ is the coupon rate, $F$ is face value, $T$ is maturity, and $r$ is the discount rate.

---

### Yield to Maturity (YTM)

The YTM is the internal rate of return $r^*$ that equates the theoretical price to the observed market price $P^{\\text{mkt}}$:

$$P^{\\text{mkt}} = \\sum_{t=1}^{T} \\frac{c \\cdot F}{(1+r^*)^t} + \\frac{F}{(1+r^*)^T}$$

This is solved numerically (e.g., via Brent's method).

---

### Zero-Coupon Bond Yield

A zero-coupon bond pays only par $F$ at maturity with no interim coupons. Its yield (spot rate) is:

$$y_t = \\left(\\frac{F}{P_t}\\right)^{1/t} - 1$$

---

### Forward Rates (No-Arbitrage)

The implied forward rate $f_{t-1,t}$ for the period from $t-1$ to $t$ satisfies:

$$(1 + y_t)^t = (1 + y_{t-1})^{t-1} \\cdot (1 + f_{t-1,t})$$

Generalising to non-unit intervals of length $\\Delta t = t_2 - t_1$:

$$f_{t_1, t_2} = \\left(\\frac{(1+y_{t_2})^{t_2}}{(1+y_{t_1})^{t_1}}\\right)^{1/\\Delta t} - 1$$

---

### Term Structure Theories

- **Expectations Hypothesis:** $f_t = E[r_{t-1,t}]$ — forward rates are unbiased forecasts of future short rates.
- **Liquidity Preference Theory:** investors prefer shorter maturities, so long-term bonds must offer a premium, causing an upward bias in forward rates and a tendency for an upward-sloping yield curve.
- **Market Segmentation:** supply and demand in each maturity segment independently determine rates.
        """)

    # ── Section 1: Bond Pricer ──────────────────────────────────────────────
    st.subheader("Bond Pricer")

    col1, col2 = st.columns(2)
    with col1:
        F = st.number_input("Par value F ($)", value=1000.0, step=100.0, min_value=1.0, key="bp_F")
        c_pct = st.number_input("Coupon rate (%)", value=5.0, step=0.25, min_value=0.0, key="bp_c")
        T_bond = st.number_input("Maturity T (years)", value=10, step=1, min_value=1, max_value=50, key="bp_T")
        r_pct = st.number_input("Discount rate / YTM (%)", value=4.0, step=0.1, key="bp_r")

    c_rate = c_pct / 100
    r = r_pct / 100
    coupon = c_rate * F
    t_arr = np.arange(1, int(T_bond) + 1)
    cash_flows = np.full(int(T_bond), coupon)
    cash_flows[-1] += F
    discount_factors = (1 + r) ** (-t_arr)
    bond_price = np.sum(cash_flows * discount_factors)

    # Price at r+1% and r-1%
    r_up = r + 0.01
    r_dn = max(r - 0.01, 0.001)
    cf_up = np.full(int(T_bond), coupon)
    cf_up[-1] += F
    cf_dn = np.full(int(T_bond), coupon)
    cf_dn[-1] += F
    price_up = np.sum(cf_up * (1 + r_up) ** (-t_arr))
    price_dn = np.sum(cf_dn * (1 + r_dn) ** (-t_arr))

    with col2:
        st.metric("Bond Price", f"${bond_price:,.2f}")
        premium_discount = "Premium" if bond_price > F else ("Discount" if bond_price < F else "Par")
        st.metric("Trades at", premium_discount)
        st.caption("A bond trades at premium when coupon rate > YTM, at discount when coupon rate < YTM.")
        c1m, c2m = st.columns(2)
        c1m.metric("Price if rate +1%", f"${price_up:,.2f}", delta=f"${price_up - bond_price:,.2f}")
        c2m.metric("Price if rate -1%", f"${price_dn:,.2f}", delta=f"${price_dn - bond_price:,.2f}")

    # Chart: bond price vs yield
    yield_range = np.linspace(0.01, 0.15, 200)
    prices_curve = []
    for y in yield_range:
        cf = np.full(int(T_bond), coupon)
        cf[-1] += F
        prices_curve.append(np.sum(cf * (1 + y) ** (-t_arr)))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(yield_range * 100, prices_curve, color="steelblue", linewidth=2, label="Bond Price")
    ax.axvline(r * 100, color="orange", linestyle="--", linewidth=1.5, label=f"Current YTM = {r * 100:.1f}%")
    ax.axhline(F, color="gray", linestyle=":", linewidth=1, label=f"Par = ${F:,.0f}")
    ax.scatter([r * 100], [bond_price], color="red", zorder=5, s=80, label=f"Price = ${bond_price:,.2f}")
    ax.set_xlabel("Yield / Discount Rate (%)")
    ax.set_ylabel("Bond Price ($)")
    ax.set_title("Bond Price vs Yield (Inverse Relationship)", fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Bond prices and yields move inversely. This is the fundamental fixed income relationship.")

    st.divider()

    # ── Section 2: YTM Calculator ───────────────────────────────────────────
    st.subheader("Yield to Maturity (YTM) Calculator")
    st.caption("YTM is the discount rate r that makes the theoretical bond price equal to the observed market price.")

    col1, col2 = st.columns(2)
    with col1:
        ytm_F = st.number_input("Par value F ($)", value=1000.0, step=100.0, key="ytm_F")
        ytm_c = st.number_input("Coupon rate (%)", value=5.0, step=0.25, key="ytm_c")
        ytm_T = st.number_input("Maturity T (years)", value=10, step=1, min_value=1, key="ytm_T")
        ytm_P = st.number_input("Market price P ($)", value=950.0, step=1.0, key="ytm_P")

    def _bond_price_fn(y, F, c, T):
        coupon_p = c * F
        t_a = np.arange(1, int(T) + 1)
        cf = np.full(int(T), coupon_p)
        cf[-1] += F
        return np.sum(cf * (1 + y) ** (-t_a)) - ytm_P

    try:
        ytm_result = brentq(_bond_price_fn, 0.0001, 0.99,
                            args=(ytm_F, ytm_c / 100, ytm_T))
        with col2:
            st.metric("YTM", f"{ytm_result * 100:.4f}%")
            rel = "above" if ytm_result > ytm_c / 100 else "below"
            st.caption(
                f"YTM ({ytm_result * 100:.2f}%) is {rel} the coupon rate ({ytm_c:.2f}%), "
                f"so the bond trades at {'discount' if ytm_result > ytm_c / 100 else 'premium'}."
            )
    except Exception:
        with col2:
            st.warning("Could not solve YTM. Check that the price is within a valid range for these parameters.")

    st.divider()

    # ── Section 3: Yield Curve Builder ─────────────────────────────────────
    st.subheader("Yield Curve & Forward Rates")
    st.caption("Enter spot yields for standard maturities. The app computes implied forward rates via no-arbitrage.")

    invert_toggle = st.checkbox("Use inverted yield curve scenario", value=False, key="yc_invert")

    default_yields = [4.5, 4.0, 3.5, 3.0, 2.8, 2.5] if invert_toggle else [2.0, 2.5, 3.0, 3.5, 3.8, 4.0]
    maturities = [1, 2, 3, 5, 7, 10]
    labels = ["1yr", "2yr", "3yr", "5yr", "7yr", "10yr"]

    cols = st.columns(6)
    yields_input = []
    for i, (col, mat, lab, def_y) in enumerate(zip(cols, maturities, labels, default_yields)):
        y = col.number_input(lab, value=float(def_y), step=0.1, min_value=0.01, max_value=20.0, key=f"yc_{i}")
        yields_input.append(y / 100)

    # Compute forward rates between adjacent maturities
    # (1+y_t2)^t2 = (1+y_t1)^t1 * (1+f_{t1,t2})^dt
    forward_rates = []
    forward_labels = []
    for i in range(1, len(maturities)):
        t1 = maturities[i - 1]
        t2 = maturities[i]
        y1 = yields_input[i - 1]
        y2 = yields_input[i]
        dt = t2 - t1
        # f = ((1+y2)^t2 / (1+y1)^t1)^(1/dt) - 1
        f = ((1 + y2) ** t2 / (1 + y1) ** t1) ** (1.0 / dt) - 1
        forward_rates.append(f * 100)
        forward_labels.append(f"{t1}–{t2}yr")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(maturities, [y * 100 for y in yields_input], "o-", color="steelblue",
            linewidth=2, markersize=6, label="Spot Yield Curve")
    mid_maturities = [(maturities[i - 1] + maturities[i]) / 2 for i in range(1, len(maturities))]
    ax.plot(mid_maturities, forward_rates, "s--", color="orange",
            linewidth=1.5, markersize=5, label="Implied Forward Rates")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Maturity (years)")
    ax.set_ylabel("Rate (%)")
    ax.set_title("Term Structure: Spot Yields & Implied Forward Rates", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Forward rates table
    fwd_df = pd.DataFrame({
        "Period": forward_labels,
        "Forward Rate (%)": [f"{f:.3f}" for f in forward_rates],
    })
    st.dataframe(fwd_df, use_container_width=False, hide_index=True)
    st.caption("Forward rates are implied by no-arbitrage. Under the expectations hypothesis, they equal expected future short rates.")

    st.divider()

    # ── Section 4: Zero-Coupon Bond Yield ───────────────────────────────────
    st.subheader("Zero-Coupon Bond Yield")
    st.caption("A zero-coupon bond pays no coupons — only par at maturity. Its yield reflects the pure time value at that horizon.")

    col1, col2 = st.columns(2)
    with col1:
        zc_F = st.number_input("Par value F ($)", value=1000.0, step=100.0, key="zc_F")
        zc_P = st.number_input("Current price P ($)", value=743.0, step=1.0, key="zc_P")
        zc_T = st.number_input("Maturity T (years)", value=5, step=1, min_value=1, key="zc_T")
    with col2:
        if zc_P > 0 and zc_F > 0 and zc_T > 0:
            zc_yield = (zc_F / zc_P) ** (1.0 / zc_T) - 1
            st.metric("Zero-Coupon Yield", f"{zc_yield * 100:.4f}%")
            st.caption(
                f"Formula: y = (F/P)^(1/T) - 1 = ({zc_F:.0f}/{zc_P:.0f})^(1/{zc_T}) - 1"
            )

            # Chart: price vs yield for zero-coupon bond
            zy_range = np.linspace(0.005, 0.15, 200)
            zc_prices = [zc_F / (1 + zy) ** zc_T for zy in zy_range]
            fig2, ax2 = plt.subplots(figsize=(7, 3))
            ax2.plot(zy_range * 100, zc_prices, color="steelblue", linewidth=2)
            ax2.scatter([zc_yield * 100], [zc_P], color="red", zorder=5, s=80,
                        label=f"Current: P=${zc_P:.0f}, y={zc_yield * 100:.2f}%")
            ax2.set_xlabel("Yield (%)")
            ax2.set_ylabel("Zero-Coupon Price ($)")
            ax2.set_title(f"Zero-Coupon Bond Price vs Yield (T={zc_T} yrs)", fontweight="bold")
            ax2.legend(fontsize=8)
            ax2.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
