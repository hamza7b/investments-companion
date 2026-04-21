import streamlit as st
import streamlit.components.v1 as components
from datetime import date
from src.home import show as show_home
from src.chapter1_intro import show as show_ch1
from src.chapter2_returns import show as show_ch2
from src.chapter3_portfolio import show as show_ch3
from src.chapter4_optimization import show as show_ch4
from src.chapter5_capm import show as show_ch5
from src.chapter6_empirics import show as show_ch6
from src.chapter7_fixed_income import show as show_ch7
from src.chapter8_duration import show as show_ch8
from src.chapter9_security import show as show_ch9
from src.chapter10_options import show as show_ch10
from src.chapter11_active import show as show_ch11
from src.chapter12_esg import show as show_ch12
from src.appendix_tvm import show as show_appendix_a

st.set_page_config(
    page_title="Investment Companion - FIN-A0104",
    page_icon="📈",
    layout="wide",
)

from src.splash import show as show_splash
if show_splash():
    st.stop()

# ── Session state init ────────────────────────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Investment Companion")
    st.caption("Computational companion to FIN-A0104 · Aalto University")
    st.divider()
    st.subheader("Primary Asset")
    ticker = st.text_input("Ticker", value="UBS")
    start_date = st.date_input("Start date", value=date(2022, 1, 1))
    end_date = st.date_input("End date", value=date(2024, 1, 1))
    st.divider()
    st.subheader("Portfolio / Optimization")
    ticker2 = st.text_input("Second ticker", value="NESN.SW")
    ticker3 = st.text_input("Third ticker", value="NOVN.SW")
    ticker4 = st.text_input("Fourth ticker (optional)", value="")
    ticker5 = st.text_input("Fifth ticker (optional)", value="")
    st.divider()
    st.subheader("Market / CAPM")
    market_ticker = st.text_input("Market index", value="^SSMI")
    risk_free_rate = st.number_input("Risk-free rate (%)", value=1.5, step=0.1) / 100
    st.divider()
    st.subheader("Options")
    option_T = st.number_input("Time to expiry (years)", value=0.5, step=0.1, min_value=0.01)
    option_r = st.number_input("Risk-free rate, % (options)", value=1.5, step=0.1) / 100
    st.divider()
    st.caption("Data sourced from Yahoo Finance via yfinance.")

shared = dict(
    ticker=ticker,
    ticker2=ticker2,
    ticker3=ticker3,
    ticker4=ticker4,
    ticker5=ticker5,
    market_ticker=market_ticker,
    start_date=start_date,
    end_date=end_date,
    risk_free_rate=risk_free_rate,
    option_T=option_T,
    option_r=option_r,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Home",
    "Ch 1 — Intro",
    "Ch 2 — Returns",
    "Ch 3 — Portfolio",
    "Ch 4 — Optimization",
    "Ch 5 — CAPM",
    "Ch 6 — Empirics",
    "Ch 7 — Fixed Income",
    "Ch 8 — Duration",
    "Ch 9 — Security Analysis",
    "Ch 10 — Options",
    "Ch 11 — Active Mgmt",
    "Ch 12 — ESG",
    "Appendix A — TVM",
])

# ── Tab auto-navigation ───────────────────────────────────────────────────────
active = st.session_state.get("active_tab", 0)
if active > 0:
    components.html(
        f'<script>setTimeout(function(){{'
        f'window.parent.document.querySelectorAll("[data-baseweb=tab]")[{active}].click();'
        f'}}, 100);</script>',
        height=0,
    )
    st.session_state["active_tab"] = 0

# ── Tab content ───────────────────────────────────────────────────────────────
with tabs[0]:  show_home()
with tabs[1]:  show_ch1()
with tabs[2]:  show_ch2(**shared)
with tabs[3]:  show_ch3(**shared)
with tabs[4]:  show_ch4(**shared)
with tabs[5]:  show_ch5(**shared)
with tabs[6]:  show_ch6(**shared)
with tabs[7]:  show_ch7(**shared)
with tabs[8]:  show_ch8(**shared)
with tabs[9]:  show_ch9(**shared)
with tabs[10]: show_ch10(**shared)
with tabs[11]: show_ch11(**shared)
with tabs[12]: show_ch12(**shared)
with tabs[13]: show_appendix_a(**shared)