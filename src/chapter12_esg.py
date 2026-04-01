import streamlit as st
import numpy as np
import pandas as pd


def show(ticker, ticker2, market_ticker, start_date, end_date, risk_free_rate, option_T, option_r):
    st.header("Chapter 12 — Sustainable Investing")
    st.caption("ESG factors, screening approaches, and the effect on cost of capital.")

    with st.expander("📖 Concept Overview", expanded=False):
        st.markdown("""
        **What is ESG?** Environmental, Social, and Governance — non-financial factors that affect
        long-run firm performance and risk.

        **Investment spectrum:** Traditional Investing → Responsible → Sustainable → Impact → Philanthropy

        **Approaches:**
        - **Negative screening:** Exclude harmful industries (tobacco, weapons, fossil fuels)
        - **Positive screening:** Overweight high-ESG-score firms
        - **Activist investing:** Engage with management to change behaviour
        - **Impact investing:** Direct capital to projects with measurable social/environmental outcomes

        **Effect on cost of capital:** ESG screening shifts capital away from unsustainable firms,
        raising their cost of capital. This may reduce their investment and output over time.
        Green firms benefit from lower financing costs.
        """)

    # ── Section 1: ESG Framework ────────────────────────────────────────────
    st.subheader("ESG Pillars")
    col_E, col_S, col_G = st.columns(3)

    with col_E:
        st.markdown("""
        ### 🌍 Environmental
        - Climate change & carbon emissions
        - Natural resource depletion
        - Waste & pollution management
        - Deforestation
        - Renewable energy adoption
        - Water usage & scarcity
        """)

    with col_S:
        st.markdown("""
        ### 👥 Social
        - Employee health & safety
        - Human rights & labour standards
        - Supply chain practices
        - Community relations
        - Data privacy & security
        - Diversity & inclusion
        """)

    with col_G:
        st.markdown("""
        ### 🏛️ Governance
        - Board composition & independence
        - Executive compensation
        - Shareholder rights
        - Transparency & disclosure
        - Anti-corruption policies
        - Audit committee quality
        """)

    st.divider()

    # Visual investment spectrum
    st.subheader("Investment Spectrum")
    st.caption("Sustainable investing sits between return-maximising and purely philanthropic objectives.")
    spectrum_cols = st.columns(5)
    labels  = ["Traditional\nInvesting", "Responsible\nInvesting", "Sustainable\nInvesting",
                "Impact\nInvesting", "Philanthropy"]
    colours = ["#4472c4", "#5b9bd5", "#70ad47", "#ffc000", "#ff0000"]
    for col, lab, clr in zip(spectrum_cols, labels, colours):
        col.markdown(
            f'<div style="background:{clr};border-radius:6px;padding:12px 6px;'
            f'text-align:center;color:white;font-size:0.82rem;font-weight:600;'
            f'min-height:64px;display:flex;align-items:center;justify-content:center">'
            f'{lab.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Section 2: Approach Simulator ───────────────────────────────────────
    st.subheader("Approach Simulator")

    approach = st.radio(
        "Choose an ESG approach:",
        ["Negative Screening", "Positive Screening", "Activist Investing", "Impact Investing"],
        horizontal=True,
        key="esg_approach",
    )

    approach_info = {
        "Negative Screening": {
            "description": "Exclude companies or industries that fail a minimum ethical or ESG standard.",
            "mechanism": "Screen out sectors: tobacco, gambling, weapons, fossil fuels. Remaining firms form the investable universe.",
            "cost_of_capital": "Unsustainable firms face higher cost of capital as capital is withdrawn. Green firms may benefit slightly.",
            "firm_behaviour": "Excluded firms lose access to capital, potentially reducing investment in harmful activities.",
            "diagram": """
```
All Firms
    │
    ▼
┌─────────────────────────────┐
│   Negative Screen           │
│   Exclude: ESG score < X    │
└────────────┬────────────────┘
             │ Pass
             ▼
     Investable Universe
     → Portfolio Weighted
```
            """,
        },
        "Positive Screening": {
            "description": "Actively overweight companies with high ESG scores relative to their industry peers.",
            "mechanism": "Rank firms by ESG score within each sector. Overweight top quartile, underweight bottom.",
            "cost_of_capital": "High-ESG firms attract more capital → lower cost of equity. Low-ESG firms face higher financing costs.",
            "firm_behaviour": "Firms have incentive to improve ESG scores to attract capital and lower their cost of financing.",
            "diagram": """
```
All Firms → ESG Scoring
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
  Top 25%   Middle 50%  Bottom 25%
Overweight   Neutral    Underweight
```
            """,
        },
        "Activist Investing": {
            "description": "Take large equity stakes and engage directly with management to improve ESG practices.",
            "mechanism": "Acquire significant shareholding → vote at AGM → engage board → push for ESG policy changes.",
            "cost_of_capital": "If activist engagement succeeds, firm ESG improves → attracts more capital → cost falls.",
            "firm_behaviour": "Management faces direct pressure to adopt sustainable practices or face shareholder revolt.",
            "diagram": """
```
Investor acquires stake
         │
         ▼
  Engage management
         │
    ┌────┴────┐
    ▼         ▼
 Success    Failure
ESG improves  → Escalate/Divest
```
            """,
        },
        "Impact Investing": {
            "description": "Direct capital to projects or companies that generate measurable positive social or environmental impact alongside financial returns.",
            "mechanism": "Target specific SDGs (e.g., clean energy, affordable housing). Measure and report impact alongside returns.",
            "cost_of_capital": "Impact projects often accept below-market returns (concessional capital) to crowd in private finance.",
            "firm_behaviour": "Creates new markets and financing channels for high-impact projects that might not access traditional capital.",
            "diagram": """
```
Capital → Impact Project
              │
    ┌─────────┴─────────┐
    ▼                   ▼
Financial Return    Social/Env. Impact
(may be below mkt)  (measured & reported)
```
            """,
        },
    }

    info = approach_info[approach]
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(f"**Description:** {info['description']}")
        st.markdown(f"**Mechanism:** {info['mechanism']}")
        st.markdown(f"**Effect on cost of capital:** {info['cost_of_capital']}")
        st.markdown(f"**Firm behaviour:** {info['firm_behaviour']}")
    with col2:
        st.markdown(info["diagram"])

    st.divider()

    # ── Section 3: Portfolio Screening Simulator ─────────────────────────────
    st.subheader("Portfolio Screening Simulator")
    st.caption("Enter hypothetical companies and their ESG scores. Apply a screen to build a filtered portfolio.")

    st.markdown("**Define 5 companies:**")
    company_names = []
    esg_scores    = []
    cols = st.columns(5)
    defaults = [
        ("TechCorp",  82),
        ("OilCo",     23),
        ("GreenEnergy", 91),
        ("RetailCo",  55),
        ("MiningCo",  31),
    ]
    for col, (def_name, def_score) in zip(cols, defaults):
        with col:
            name  = st.text_input("Company", value=def_name, key=f"esg_name_{def_name}")
            score = st.number_input("ESG Score (0–100)", value=float(def_score), min_value=0.0,
                                    max_value=100.0, step=1.0, key=f"esg_score_{def_name}")
        company_names.append(name)
        esg_scores.append(score)

    screen_type = st.radio("Screening type:", ["Negative (exclude below threshold)", "Positive (include above threshold)"],
                           horizontal=True, key="esg_screen_type")
    threshold = st.slider("ESG threshold", 0, 100, 50, key="esg_threshold")

    # Apply screen
    passing = []
    for name, score in zip(company_names, esg_scores):
        passes = (score >= threshold) if "Positive" in screen_type else (score >= threshold)
        # Negative screening: exclude below threshold means exclude if score < threshold
        if "Negative" in screen_type:
            passes = score >= threshold
        else:
            passes = score >= threshold
        passing.append(passes)

    n_passing = sum(passing)
    equal_weight = 1.0 / n_passing if n_passing > 0 else 0.0

    results_df = pd.DataFrame({
        "Company": company_names,
        "ESG Score": esg_scores,
        "Passes Screen": ["✅ Yes" if p else "❌ No" for p in passing],
        "Portfolio Weight": [f"{equal_weight*100:.1f}%" if p else "—" for p in passing],
    })
    st.dataframe(results_df, use_container_width=True, hide_index=True)

    if n_passing == 0:
        st.warning("No companies pass the screen. Lower the threshold.")
    else:
        st.success(f"{n_passing} of {len(company_names)} companies pass. Equal-weighted portfolio: {equal_weight*100:.1f}% each.")
        avg_esg_portfolio = np.mean([s for s, p in zip(esg_scores, passing) if p])
        st.metric("Portfolio Average ESG Score", f"{avg_esg_portfolio:.1f}")
