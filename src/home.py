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
        '<div class="cc-hero-sub">FIN-A0104 · Fundamentals of Investments · Aalto University</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1.6, 1, 1])

    with col_a:
        st.markdown(
            '<div class="cc-body-text">'
            "This tool translates every quantitative model in the FIN-A0104 lecture notes into "
            "live, interactive calculators driven by real market data. Enter a ticker, pick a date "
            "range, and explore the formulas in action — chapter by chapter."
            "</div>",
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            '<div style="background:var(--secondary-background-color);border-radius:8px;padding:14px 16px">'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#00d4aa;margin-bottom:8px">Covers</div>'
            '<div class="cc-body-text" style="font-size:0.88rem;line-height:1.9">'
            "✦ Returns &amp; Risk<br>"
            "✦ Portfolio Theory<br>"
            "✦ CAPM &amp; Multifactor<br>"
            "✦ Fixed Income &amp; Options"
            "</div></div>",
            unsafe_allow_html=True,
        )

    with col_c:
        st.markdown(
            '<div style="background:var(--secondary-background-color);border-radius:8px;padding:14px 16px">'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#58a6ff;margin-bottom:8px">How to use</div>'
            '<div class="cc-body-text" style="font-size:0.88rem;line-height:1.9">'
            "1. Set ticker &amp; dates in the sidebar<br>"
            "2. Navigate tabs per chapter<br>"
            "3. Adjust parameters live<br>"
            "4. Read formulas in each expander"
            "</div></div>",
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
