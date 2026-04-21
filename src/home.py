"""Home page — app overview and course chapter map.
No financial content; purely navigational/informational.
Renders via show() called from app.py.
"""

import streamlit as st

CSS = """
<style>
.cc-hero-wrap {
    text-align: center;
    padding: 3rem 1rem 2.5rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    margin-bottom: 0;
    width: 100%; 
    max-width: 100%;
}
.cc-hero-icon {
    width: 64px; height: 64px;
    background: rgba(0,212,170,0.1);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1.5rem;
    font-size: 28px;
}
.cc-hero-title {
    font-size: 2.6rem; font-weight: 700;
    color: var(--text-color);
    margin-bottom: 0.5rem;
}
.cc-hero-sub {
    font-size: 1.1rem;
    color: color-mix(in srgb, var(--text-color) 45%, transparent);
    margin-bottom: 1.25rem;
}
.cc-hero-desc {
    font-size: 0.95rem;
    color: color-mix(in srgb, var(--text-color) 70%, transparent);
    max-width: 1000px;
    margin: 0 auto;
    line-height: 1.75;
}
.cc-section-wrap {
    padding: 2.5rem 0;
    border-bottom: none;
}
.cc-section-title {
    font-size: 1.7rem; font-weight: 700;
    color: var(--text-color);
    text-align: center;
    margin-bottom: 2rem;
}
.cc-step-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 12px;
}
.cc-step-num {
    width: 40px; height: 40px; min-width: 40px;
    background: #00d4aa;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700;
    color: #0a1a15;
}
.cc-step-body { flex: 1; }
.cc-step-title {
    font-size: 1rem; font-weight: 600;
    color: var(--text-color);
    margin-bottom: 4px;
}
.cc-step-desc {
    font-size: 0.85rem;
    color: color-mix(in srgb, var(--text-color) 55%, transparent);
    line-height: 1.5;
}
.cc-map-wrap { 
    padding: 2.5rem 0;
    border-bottom: 1px solid rgba(128, 128, 128, 0.3);  /* Changed from border-top to border-bottom */
}

/* Part title styling */
.cc-part-title {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    padding: 4px 0 6px 0;
    border-bottom: 1px solid rgba(128, 128, 128, 0.3);
    margin-bottom: 10px;
}

/* Add bottom border to each column's content (separates parts) */
[data-testid="column"] > div {
    border-bottom: 1px solid rgba(128, 128, 128, 0.25);
    padding-bottom: 1rem;
    margin-bottom: 1rem;
}

/* Remove border from last child to avoid double border */
[data-testid="column"] > div:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

/* Chapter card styling */
.chapter-card {
    background: var(--secondary-background-color);
    border-radius: 8px;
    padding: 14px 16px;
    border-left: 4px solid;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.chapter-num {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    width: 36px; min-width: 36px;
    margin-top: 2px;
}
.chapter-title {
    font-size: 0.95rem; font-weight: 600;
    color: var(--text-color);
    margin-bottom: 3px;
}
.chapter-desc {
    font-size: 0.82rem;
    color: color-mix(in srgb, var(--text-color) 55%, transparent);
    line-height: 1.4;
}

/* Arrow button styling */
.stButton > button {
    background: var(--secondary-background-color) !important;
    border: none !important;
    border-radius: 8px !important;
    width: 44px !important;
    height: 100% !important;
    min-height: 70px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
    padding: 0 !important;
    margin: 0 !important;
}
.stButton > button:hover {
    transform: translateX(3px) !important;
    background: rgba(0, 0, 0, 0.05) !important;
    border: none !important;
}
.stButton > button:focus {
    outline: none !important;
}

/* Footer - removed the duplicate line */
.cc-footer {
    padding: 1.75rem 0;
    text-align: center;
    font-size: 0.82rem;
    color: color-mix(in srgb, var(--text-color) 40%, transparent);
    border-top: none;  /* Remove border from footer */
}
.cc-footer strong {
    color: color-mix(in srgb, var(--text-color) 65%, transparent);
    font-weight: 500;
}
.cc-footer em {
    font-style: italic;
    font-size: 0.78rem;
}

/* Light mode specific adjustments */
@media (prefers-color-scheme: light) {
    [data-testid="column"] > div {
        border-bottom-color: rgba(0, 0, 0, 0.15);
    }
    .cc-part-title {
        border-bottom-color: rgba(0, 0, 0, 0.15);
    }
    .cc-map-wrap {
        border-bottom-color: rgba(0, 0, 0, 0.15);
    }
    .stButton > button:hover {
        background: rgba(0, 0, 0, 0.03) !important;
    }
}
</style>
"""

PARTS = [
    {
        "label": "Part I — Fundamentals",
        "key": "fundamentals",
        "chapters": [
            ("Ch 1",  "Introduction",                   "Markets, securities, trading mechanics, and the investment process.",            1),
            ("Ch 2",  "Return, Expected Return & Risk", "Simple and log returns, expected return, variance, and volatility.",             2),
            ("Ch 3",  "Portfolio Theory",               "Two-asset portfolios, covariance, diversification, and the efficient frontier.", 3),
        ],
    },
    {
        "label": "Part II — Portfolio Theory",
        "key": "portfolio",
        "chapters": [
            ("Ch 4",  "Optimal Risky Portfolio", "Mean-variance optimisation, the Sharpe-optimal portfolio, and the CML.", 4),
            ("Ch 5",  "CAPM & Beta Estimation",  "Systematic risk, beta, the SML, and Jensen's alpha.",                   5),
            ("Ch 6",  "Multifactor Models",       "APT, Fama-French factors, and characteristic-based models.",            6),
        ],
    },
    {
        "label": "Part III — Asset Pricing",
        "key": "pricing",
        "chapters": [
            ("Ch 7",  "Efficient Markets",       "EMH, weak/semi-strong/strong forms, and market anomalies.",              7),
            ("Ch 8",  "Behavioural Finance",     "Cognitive biases, limits to arbitrage, and investor behaviour.",         8),
            ("Ch 9",  "Fixed Income Securities", "Bond pricing, duration, convexity, and the term structure.",             9),
            ("Ch 10", "Option Pricing",          "Black-Scholes model, put-call parity, Greeks, and implied volatility.", 10),
        ],
    },
    {
        "label": "Part IV — Applications",
        "key": "applications",
        "chapters": [
            ("Ch 11", "Active Portfolio Management", "Information ratio, Treynor-Black model, and active vs passive strategies.", 11),
            ("Ch 12", "Performance Evaluation",      "Sharpe, Treynor, Jensen, M², and attribution analysis.",                  12),
        ],
    },
    {
        "label": "Appendices",
        "key": "appendices",
        "chapters": [
            ("App A", "Statistics Review",   "Expectation, variance, covariance, correlation, and OLS regression.",  13),
            ("App B", "Time Value of Money", "Present value, future value, annuities, and continuous compounding.", 13),
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

STEPS = [
    ("Set your data",        "Enter a primary ticker (e.g. <code>UBS</code>), a second ticker, a market index, and a date range in the <strong>sidebar</strong>."),
    ("Pick a chapter",       "Click any <strong>tab</strong> at the top to open that chapter or in the course map. Each tab is fully self-contained."),
    ("Read the overview",    "Open the <strong>📖 Concept Overview</strong> expander to see the formulas and theory before diving into results."),
    ("Interact with inputs", "Adjust sliders, number inputs, and dropdowns to see how outputs respond in real time."),
    ("Interpret the output", "Every metric has a <strong>caption</strong> below it explaining what it means and how to read it."),
]


def _step_card(num: int, title: str, desc: str) -> str:
    return (
        f'<div class="cc-step-card">'
        f'  <div class="cc-step-num">{num}</div>'
        f'  <div class="cc-step-body">'
        f'    <div class="cc-step-title">{title}</div>'
        f'    <div class="cc-step-desc">{desc}</div>'
        f'  </div>'
        f'</div>'
    )


def show():
    st.markdown(CSS, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="cc-hero-wrap">'
        '  <div class="cc-hero-icon">🏦</div>'
        '  <div class="cc-hero-title">Computational Companion</div>'
        '  <div class="cc-hero-sub">FIN-A0104 · Fundamentals of Investments · Aalto University School of Business</div>'
        '  <div class="cc-hero-desc">'
        "    This tool translates every quantitative model in the FIN-A0104 lecture notes into "
        "    live, interactive calculators driven by real market data from Yahoo Finance. "
        "    Enter a ticker and date range in the sidebar, then explore returns, portfolio theory, "
        "    asset pricing, fixed income, options, and more — each chapter as a standalone tab, "
        "    with full formulas and explanations alongside the results."
        '  </div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── How to Use ────────────────────────────────────────────────────────────
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cc-section-title">How to Use ? </div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    for i, (title, desc) in enumerate(STEPS):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(_step_card(i + 1, title, desc), unsafe_allow_html=True)

    

    # ── Course Map ────────────────────────────────────────────────────────────
    st.markdown('<div class="cc-map-wrap">', unsafe_allow_html=True)
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cc-section-title">Course Map</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.95rem; text-align:center; margin-top:0.5rem; margin-bottom:2rem;'
        ' color:color-mix(in srgb, var(--text-color) 55%, transparent);">'
        'The companion follows the course structure. Click the arrow next to any chapter to open it.'
        '</div>',
        unsafe_allow_html=True,
    )


    # Create three columns for the course map layout
    col_a, col_b, col_c = st.columns(3, gap="large")
    col_assignments = [col_a, col_b, col_c, col_a, col_b]

    for part, col in zip(PARTS, col_assignments):
        colour = PART_COLOURS[part["key"]]
        with col:
            st.markdown(
                f'<div class="cc-part-title" style="color:{colour}">{part["label"]}</div>',
                unsafe_allow_html=True,
            )
            for num, title, desc, tab_index in part["chapters"]:
                # Create a unique key for this chapter
                unique_key = f"nav_{tab_index}_{num}_{title.replace(' ', '_').replace('&', '')}"
                
                # Use columns to align card and button
                card_col, btn_col = st.columns([10, 1])
                
                with card_col:
                    # Card content
                    st.markdown(
                        f'<div class="chapter-card" style="border-left-color:{colour}">'
                        f'  <div class="chapter-num" style="color:{colour}">{num}</div>'
                        f'  <div style="flex:1">'
                        f'    <div class="chapter-title">{title}</div>'
                        f'    <div class="chapter-desc">{desc}</div>'
                        f'  </div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                
                with btn_col:
                    # Button with color matching
                    button_style = f"""
                        <style>
                        button[key="{unique_key}"] {{
                            color: {colour} !important;
                        }}
                        </style>
                    """
                    st.markdown(button_style, unsafe_allow_html=True)
                    if st.button("→", key=unique_key, use_container_width=True):
                        st.session_state["active_tab"] = tab_index
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Credits ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='cc-divider'>", unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-footer">'
        "Based on lecture notes by <strong>Prof. Petri Jylhä</strong> · "
        "Aalto University School of Business · FIN-A0104<br>"
        "<em>An independent computational extension — not official course material.</em>"
        '</div>',
        unsafe_allow_html=True,
    )