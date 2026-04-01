"""
Home page — app overview and course chapter map.
No financial content; purely navigational/informational.
Renders via show() called from app.py.
"""

import streamlit as st


CSS = """
<style>
.cc-hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: var(--text-color);
    margin-bottom: 0.1rem;
}
.cc-hero-sub {
    font-size: 1.05rem;
    color: color-mix(in srgb, var(--text-color) 55%, transparent);
    margin-bottom: 0;
}
.cc-step-box {
    background: var(--secondary-background-color);
    border-radius: 8px;
    padding: 14px 18px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 10px;
}
.cc-step-num {
    font-size: 0.78rem;
    font-weight: 800;
    color: #00d4aa;
    background: rgba(0,212,170,0.12);
    border-radius: 50%;
    width: 26px;
    height: 26px;
    min-width: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1px;
}
.cc-step-text {
    font-size: 0.9rem;
    color: color-mix(in srgb, var(--text-color) 80%, transparent);
    line-height: 1.5;
}
.cc-step-text strong {
    color: var(--text-color);
}
.cc-section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #00d4aa;
    margin-bottom: 0.6rem;
}
.cc-section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 0.25rem;
}
.cc-section-desc {
    font-size: 0.95rem;
    color: color-mix(in srgb, var(--text-color) 55%, transparent);
    margin-bottom: 1.5rem;
}
.cc-body-text {
    font-size: 0.95rem;
    color: color-mix(in srgb, var(--text-color) 85%, transparent);
    line-height: 1.7;
}
.cc-card {
    background: var(--secondary-background-color);
    border-radius: 8px;
    padding: 14px 16px 12px 16px;
    margin-bottom: 10px;
    border-left: 3px solid #00d4aa;
    line-height: 1.4;
}
.cc-card-num {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.cc-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 3px;
}
.cc-card-desc {
    font-size: 0.82rem;
    color: color-mix(in srgb, var(--text-color) 55%, transparent);
}
.cc-part-header {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    padding: 4px 0 6px 0;
    border-bottom: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
    margin-bottom: 10px;
}
.cc-divider {
    border: none;
    border-top: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
    margin: 2rem 0;
}
</style>
"""

PARTS = [
    {
        "label": "Part I — Fundamentals",
        "key": "fundamentals",
        "chapters": [
            ("Ch 1",  "Introduction",                   "Markets, securities, trading mechanics, and the investment process."),
            ("Ch 2",  "Return, Expected Return & Risk", "Simple and log returns, expected return, variance, and volatility."),
            ("Ch 3",  "Portfolio Theory",               "Two-asset portfolios, covariance, diversification, and the efficient frontier."),
        ],
    },
    {
        "label": "Part II — Portfolio Theory",
        "key": "portfolio",
        "chapters": [
            ("Ch 4",  "Optimal Risky Portfolio", "Mean-variance optimisation, the Sharpe-optimal portfolio, and the CML."),
            ("Ch 5",  "CAPM & Beta Estimation",  "Systematic risk, beta, the SML, and Jensen's alpha."),
            ("Ch 6",  "Multifactor Models",       "APT, Fama-French factors, and characteristic-based models."),
        ],
    },
    {
        "label": "Part III — Asset Pricing",
        "key": "pricing",
        "chapters": [
            ("Ch 7",  "Efficient Markets",       "EMH, weak/semi-strong/strong forms, and market anomalies."),
            ("Ch 8",  "Behavioural Finance",     "Cognitive biases, limits to arbitrage, and investor behaviour."),
            ("Ch 9",  "Fixed Income Securities", "Bond pricing, duration, convexity, and the term structure."),
            ("Ch 10", "Option Pricing",          "Black-Scholes model, put-call parity, Greeks, and implied volatility."),
        ],
    },
    {
        "label": "Part IV — Applications",
        "key": "applications",
        "chapters": [
            ("Ch 11", "Active Portfolio Management", "Information ratio, Treynor-Black model, and active vs passive strategies."),
            ("Ch 12", "Performance Evaluation",      "Sharpe, Treynor, Jensen, M², and attribution analysis."),
        ],
    },
    {
        "label": "Appendices",
        "key": "appendices",
        "chapters": [
            ("App A", "Statistics Review",   "Expectation, variance, covariance, correlation, and OLS regression."),
            ("App B", "Time Value of Money", "Present value, future value, annuities, and continuous compounding."),
        ],
    },
]

PART_COLOURS = {
    "fundamentals": "#00d4aa",
    "portfolio":    "#58a6ff",
    "pricing":      "#c89a5a",
    "applications": "#bc8cff",
    "appendices":   "#8b949e",
}


def _chapter_card(num: str, title: str, desc: str, colour: str) -> str:
    return (
        f'<div class="cc-card" style="border-left-color:{colour}">'
        f'  <div class="cc-card-num" style="color:{colour}">{num}</div>'
        f'  <div class="cc-card-title">{title}</div>'
        f'  <div class="cc-card-desc">{desc}</div>'
        f'</div>'
    )


def _part_header(label: str, colour: str) -> str:
    return f'<div class="cc-part-header" style="color:{colour}">{label}</div>'


def show():
    st.markdown(CSS, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="cc-hero-title">Computational Companion</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-hero-sub">FIN-A0104 · Fundamentals of Investments · Aalto University School of Business</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Introduction ──────────────────────────────────────────────────────────
    st.markdown('<div class="cc-section-label">Introduction</div>', unsafe_allow_html=True)

    col_intro, col_covers = st.columns([1.8, 1], gap="large")
    with col_intro:
        st.markdown(
            '<div class="cc-body-text">'
            "This tool translates every quantitative model in the FIN-A0104 lecture notes into "
            "live, interactive calculators driven by real market data from Yahoo Finance. "
            "Enter a ticker and date range in the sidebar, then explore returns, portfolio theory, "
            "asset pricing, fixed income, options, and more — each chapter as a standalone tab, "
            "with full formulas and explanations alongside the results."
            "<br><br>"
            "Built as an independent computational extension of the course. "
            "Not official Aalto course material."
            "</div>",
            unsafe_allow_html=True,
        )
    with col_covers:
        st.markdown(
            '<div style="background:var(--secondary-background-color);border-radius:8px;padding:16px 18px">'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#00d4aa;margin-bottom:10px">Covers</div>'
            '<div class="cc-body-text" style="font-size:0.88rem;line-height:2.0">'
            "✦ Returns &amp; Risk<br>"
            "✦ Portfolio Theory &amp; Optimization<br>"
            "✦ CAPM, Beta &amp; Multifactor Models<br>"
            "✦ Fixed Income &amp; Duration<br>"
            "✦ Options &amp; Black-Scholes<br>"
            "✦ Active Management &amp; ESG"
            "</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='cc-divider'>", unsafe_allow_html=True)

    # ── How to use ────────────────────────────────────────────────────────────
    st.markdown('<div class="cc-section-label">How to Use</div>', unsafe_allow_html=True)

    steps = [
        ("Set your data",        "Enter a primary ticker (e.g. <code>UBS</code>), a second ticker, a market index, and a date range in the <strong>sidebar</strong>."),
        ("Pick a chapter",       "Click any <strong>tab</strong> at the top to open that chapter. Each tab is fully self-contained."),
        ("Read the overview",    "Open the <strong>📖 Concept Overview</strong> expander to see the formulas and theory before diving into results."),
        ("Interact with inputs", "Adjust sliders, number inputs, and dropdowns to see how outputs respond in real time."),
        ("Interpret the output", "Every metric has a <strong>caption</strong> below it explaining what it means and how to read it."),
    ]

    col1, col2 = st.columns(2, gap="large")
    for i, (title, body) in enumerate(steps):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(
                f'<div class="cc-step-box">'
                f'  <div class="cc-step-num">{i+1}</div>'
                f'  <div class="cc-step-text"><strong>{title}</strong><br>{body}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Credits ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='cc-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="cc-section-label">Credits</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-body-text" style="font-size:0.88rem;line-height:1.9;color:color-mix(in srgb,var(--text-color) 60%,transparent)">'
        "Based on lecture notes by <strong style='color:var(--text-color)'>Prof. Petri Jylhä</strong> · "
        "Aalto University School of Business · FIN-A0104<br>"
        "<span style='font-size:0.8rem;font-style:italic'>"
        "An independent computational extension — not official course material."
        "</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Chapter map ───────────────────────────────────────────────────────────
    st.markdown("<hr class='cc-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="cc-section-label">Course Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="cc-section-title">All Chapters at a Glance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-section-desc">The companion follows the course structure. '
        "Tabs in this app correspond to the chapters marked as implemented.</div>",
        unsafe_allow_html=True,
    )

    left_parts  = PARTS[:3]  # Fundamentals, Portfolio Theory, Asset Pricing
    right_parts = PARTS[3:]  # Applications, Appendices

    col_left, col_right = st.columns(2, gap="large")

    for col, parts in ((col_left, left_parts), (col_right, right_parts)):
        with col:
            for part in parts:
                colour = PART_COLOURS[part["key"]]
                html = _part_header(part["label"], colour)
                for num, title, desc in part["chapters"]:
                    html += _chapter_card(num, title, desc, colour)
                html += "<br>"
                st.markdown(html, unsafe_allow_html=True)
