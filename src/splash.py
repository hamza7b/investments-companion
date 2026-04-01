"""
Splash screen for Investment Companion app.
Renders as normal page content (no fixed overlay) so the Enter button
is always visible and clickable.
"""

import streamlit as st


def show() -> bool:
    """
    Display splash screen on first session load.

    Returns True  → splash is active; caller should st.stop().
    Returns False → user has already entered; render the main app.
    """
    if "splash_shown" not in st.session_state:
        st.session_state.splash_shown = True

    if not st.session_state.splash_shown:
        return False

    # Hide sidebar and tab bar while splash is showing
    st.markdown("""
    <style>
    section[data-testid="stSidebar"]  { display: none !important; }
    [data-testid="stDecoration"]      { display: none !important; }

    /* Vertically centre the content */
    .splash-outer {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 65vh;
        text-align: center;
    }
    .splash-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: var(--text-color);
        line-height: 1.1;
        margin-bottom: 0.6rem;
    }
    .splash-sub {
        font-size: 1.05rem;
        font-weight: 500;
        color: color-mix(in srgb, var(--text-color) 60%, transparent);
        margin-bottom: 0.3rem;
    }
    .splash-university {
        font-size: 0.9rem;
        color: color-mix(in srgb, var(--text-color) 45%, transparent);
        margin-bottom: 0;
    }
    .splash-divider {
        width: 48px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00d4aa, transparent);
        margin: 1.6rem auto;
    }
    .splash-prof {
        font-size: 0.88rem;
        font-style: italic;
        color: color-mix(in srgb, var(--text-color) 60%, transparent);
        margin-bottom: 0.35rem;
    }
    .splash-dev {
        font-size: 0.78rem;
        font-style: italic;
        color: color-mix(in srgb, var(--text-color) 38%, transparent);
        margin-bottom: 0;
    }
    .splash-disclaimer {
        font-size: 0.72rem;
        color: color-mix(in srgb, var(--text-color) 28%, transparent);
        margin-bottom: 0;
    }

    /* Style the Streamlit button to look like a CTA */
    div[data-testid="stButton"] > button {
        background: #00d4aa !important;
        color: #0f1117 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.65rem 2.8rem !important;
        border-radius: 6px !important;
        border: none !important;
        letter-spacing: 0.04em !important;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="splash-outer">
        <div class="splash-title">Computational Companion</div>
        <div class="splash-sub">FIN-A0104 · Fundamentals of Investments</div>
        <div class="splash-university">Aalto University</div>
        <div class="splash-divider"></div>
        <div class="splash-prof">Based on lecture notes by Prof. Petri Jylhä</div>
        <div class="splash-dev">Developed by Hamza Bichiou</div>
        <div class="splash-divider"></div>
        <div class="splash-disclaimer">An independent computational extension — not official course material</div>
    </div>
    """, unsafe_allow_html=True)

    # Button — rendered as a real Streamlit widget, never hidden by an overlay
    _, col, _ = st.columns([2, 1, 2])
    with col:
        if st.button("Enter →", use_container_width=True, key="splash_enter"):
            st.session_state.splash_shown = False
            st.rerun()

    return True
