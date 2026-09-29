"""
Customer Intelligence Dashboard — Enhanced Edition
Gus Bavia-inspired design with sidebar navigation and interactive insight cards.

Place these THREE CSV files in the same folder as app.py:
    transactions_with_segments.csv
    returns_data.csv
    guests_data.csv

Run:
    streamlit run app_enhanced.py
"""

import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Customer Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode


st.session_state.setdefault("dark_mode", False)
dark_mode = st.session_state.dark_mode

# =============================================================================
# DESIGN TOKENS
# =============================================================================
C = (
    {
        "bg": "#303A37",
        "card": "#3D4945",
        "card_hover": "#475550",
        "white": "#FFFFFF",
        "orange": "#72C6B9",
        "orange_light": "#91D8CE",
        "action": "#216F66",
        "action_light": "#2D8377",
        "selection_bg": "#526E67",
        "selection_ink": "#F6F7F5",
        "selection_border": "#7AC7B9",
        "accent_rgb": "114, 198, 185",
        "ink": "#F6F7F5",
        "muted": "#C2CDC9",
        "line": "#5C6964",
        "green": "#A0C68E",
        "red": "#EA858C",
        "gold": "#E6BE6C",
        "blue": "#91B9E7",
        "teal": "#79C5C5",
    }
    if dark_mode
    else {
        "bg": "#F4F6F8",
        "card": "#FFFFFF",
        "card_hover": "#F8FAFB",
        "white": "#FFFFFF",
        "orange": "#176B64",
        "orange_light": "#247E75",
        "action": "#176B64",
        "action_light": "#247E75",
        "selection_bg": "#E1F1ED",
        "selection_ink": "#185F58",
        "selection_border": "#A8D0C7",
        "accent_rgb": "23, 107, 100",
        "ink": "#202831",
        "muted": "#65717D",
        "line": "#DCE3E8",
        "green": "#4E7A5D",
        "red": "#B84D5A",
        "gold": "#A8782F",
        "blue": "#4F74A8",
        "teal": "#267C83",
    }
)


def color_rgba(color, alpha):
    channels = (int(color[index:index + 2], 16) for index in (1, 3, 5))
    return f"rgba({', '.join(str(channel) for channel in channels)}, {alpha})"


SEGMENT_COLOR = {
    "Champions": C["gold"],
    "Loyal Customers": C["teal"],
    "At Risk": C["red"],
}

CHART_COLORWAY = [C["gold"], C["teal"], C["red"], C["blue"], C["green"]]

SEGMENT_TINT = {
    name: color_rgba(color, 0.15)
    for name, color in SEGMENT_COLOR.items()
}

SEGMENT_ACTIONS = {
    "Champions": ["Premium loyalty", "Early access", "VIP support"],
    "Loyal Customers": ["Loyalty rewards", "Cross-sell", "Engagement email"],
    "At Risk": ["Win-back campaign", "Personalized offer", "Reactivation"],
}

SEGMENT_NOTE = {
    "Champions": "High-value customers with the strongest current RFM profile.",
    "Loyal Customers": "The recurring-value core with room to deepen engagement.",
    "At Risk": "Customers with a longer purchase gap and a clear reactivation opportunity.",
}

# =============================================================================
# GLOBAL CSS (Theme + Hover Effects)
# =============================================================================
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');

:root {{
    --bg: {C['bg']};
    --card: {C['card']};
    --card-hover: {C['card_hover']};
    --orange: {C['orange']};
    --orange-light: {C['orange_light']};
    --action: {C['action']};
    --action-light: {C['action_light']};
    --selection-bg: {C['selection_bg']};
    --selection-ink: {C['selection_ink']};
    --selection-border: {C['selection_border']};
    --ink: {C['ink']};
    --muted: {C['muted']};
    --line: {C['line']};
}}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
    background-color: var(--bg);
}}

.stApp {{
    background-color: var(--bg);
}}

#MainMenu, footer {{
    visibility: hidden;
}}

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

button[data-testid="stExpandSidebarButton"] {{
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 1001 !important;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    padding: 0 !important;
    border: 1px solid var(--line) !important;
    border-radius: 50% !important;
    background: var(--card) !important;
    color: var(--orange) !important;
    box-shadow: 0 5px 16px rgba(32, 40, 49, 0.16) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
}}

button[data-testid="stExpandSidebarButton"] span {{
    color: var(--orange) !important;
    font-size: 22px !important;
}}

button[data-testid="stExpandSidebarButton"]:hover {{
    transform: translateY(-2px) rotate(4deg) !important;
    background: var(--card-hover) !important;
    box-shadow: 0 8px 20px rgba({C['accent_rgb']}, 0.22) !important;
}}

button[data-testid="stExpandSidebarButton"]:active {{
    transform: scale(0.94) !important;
}}

button[data-testid="stExpandSidebarButton"]:focus-visible {{
    outline: 3px solid rgba({C['accent_rgb']}, 0.3) !important;
    outline-offset: 3px !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] {{
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    padding: 0 !important;
    border: 1px solid var(--line) !important;
    border-radius: 50% !important;
    background: var(--card) !important;
    color: var(--orange) !important;
    box-shadow: 0 4px 12px rgba({C['accent_rgb']}, 0.16) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] span {{
    color: var(--orange) !important;
    font-size: 20px !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"]:hover {{
    transform: translateY(-2px) rotate(-4deg) !important;
    background: var(--card-hover) !important;
    box-shadow: 0 7px 16px rgba({C['accent_rgb']}, 0.24) !important;
}}

.st-key-theme-toggle button {{
    width: 40px;
    height: 40px;
    min-height: 40px;
    padding: 0;
    border: 1px solid var(--line);
    border-radius: 50%;
    background: var(--card);
    color: var(--orange);
    box-shadow: 0 5px 16px rgba(32, 40, 49, 0.14);
    font-size: 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}}

.st-key-theme-toggle button:hover {{
    transform: translateY(-2px) rotate(8deg);
    background: var(--card-hover);
    box-shadow: 0 8px 20px rgba({C['accent_rgb']}, 0.2);
}}

.st-key-theme-toggle button:active {{
    transform: scale(0.94);
}}

.block-container {{
    padding: 2rem 2.5rem 3rem;
    max-width: 1600px;
}}

h1, h2, h3, .serif {{
    font-family: 'Playfair Display', serif !important;
}}

/* ===== SIDEBAR NAVIGATION ===== */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {C['card']} 0%, {C['card']} 100%);
    border-right: 1px solid var(--line);
}}

section[data-testid="stSidebar"] > div {{
    padding: 2rem 1rem 1rem;
}}

.brand {{
    display: flex;
    gap: 12px;
    align-items: center;
    margin: 0 5px 40px;
    padding: 20px;
    border-bottom: 1px solid var(--line);
}}

.brand-icon {{
    width: 50px;
    height: 50px;
    border-radius: 12px;
    background: var(--action);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    font-weight: 700;
}}

.brand-title {{
    color: var(--ink);
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    line-height: 1.1;
    font-weight: 600;
}}

.brand-sub {{
    color: var(--muted);
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    margin-top: 4px;
    text-transform: uppercase;
}}

.nav-label {{
    color: var(--muted);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 20px 10px 12px;
    font-weight: 700;
}}

/* Radio buttons styled as nav items */
section[data-testid="stSidebar"] div[role="radiogroup"] {{
    gap: 8px;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    width: 100%;
    min-height: 50px;
    padding: 12px 16px !important;
    margin: 0 !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    color: var(--muted) !important;
    background: transparent !important;
    transition: all 0.25s ease !important;
    cursor: pointer;
    display: flex;
    align-items: center;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: var(--card-hover) !important;
    color: var(--orange-light) !important;
    border-color: var(--orange) !important;
    transform: translateX(6px);
    padding-left: 22px !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
    background: var(--action) !important;
    color: white !important;
    border-color: var(--action) !important;
    box-shadow: 0 10px 30px rgba({C['accent_rgb']}, 0.25);
    padding-left: 22px !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {{
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] label input {{
    display: none;
}}

.sidebar-help {{
    margin: 40px 10px 12px;
    padding: 16px;
    border-radius: 12px;
    background: var(--card-hover);
    border: 1px solid var(--line);
}}

.sidebar-help-title {{
    color: var(--orange);
    font-weight: 700;
    font-size: 0.8rem;
    margin: 0 0 8px 0;
}}

.sidebar-help-text {{
    color: var(--muted);
    font-size: 0.7rem;
    line-height: 1.6;
    margin: 0;
}}

.sidebar-foot {{
    color: var(--muted);
    font-size: 0.65rem;
    text-align: center;
    margin-top: 20px;
}}

/* ===== HEADER ===== */
.header {{
    display: flex;
    justify-content: space-between;
    gap: 25px;
    align-items: flex-start;
    margin-bottom: 30px;
}}

body:has(button[data-testid="stExpandSidebarButton"]) .header {{
    padding-left: 54px;
}}

.page-title {{
    margin: 0;
    color: var(--ink);
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    line-height: 1.1;
    font-weight: 600;
}}

.page-subtitle {{
    color: var(--muted);
    font-size: 0.9rem;
    margin: 8px 0 0;
}}

.rule {{
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--orange), transparent);
    margin: 24px 0 28px;
}}

/* ===== FILTERS ===== */
.filter-bar {{
    display: flex;
    gap: 20px;
    margin-bottom: 32px;
    align-items: flex-end;
    flex-wrap: wrap;
}}

.filter-group {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.filter-label {{
    color: var(--muted);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
}}

/* Dropdown select styling */
div[data-baseweb="select"] {{
    min-width: 220px;
}}

div[data-baseweb="select"] > div {{
    background-color: var(--card) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    min-height: 44px;
    transition: all 0.2s ease;
}}

.st-key-filter-segment,
.st-key-filter-country,
.st-key-filter-date {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 12px 14px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}

.st-key-filter-segment:hover,
.st-key-filter-country:hover,
.st-key-filter-date:hover {{
    border-color: var(--orange);
    box-shadow: 0 8px 20px rgba(32, 40, 49, 0.07);
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"],
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"] {{
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    scrollbar-width: thin;
    scrollbar-color: var(--muted) transparent;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"] [role="group"],
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"] [role="group"] {{
    flex: 0 0 max-content !important;
    width: max-content !important;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"] [role="group"] > span,
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"] [role="group"] > span {{
    flex: 0 0 auto !important;
    max-width: none !important;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"] [role="group"] > span > span,
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"] [role="group"] > span > span {{
    max-width: none !important;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar,
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar {{
    height: 4px;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar-thumb,
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar-thumb {{
    background: var(--muted);
    border-radius: 4px;
}}

.st-key-filter-segment div[role="group"],
.st-key-filter-country div[role="group"] {{
    background: var(--card) !important;
    border-color: var(--line) !important;
    color: var(--ink) !important;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"] [role="group"] > span,
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"] [role="group"] > span {{
    background: var(--selection-bg) !important;
    border: 1px solid var(--selection-border) !important;
    color: var(--selection-ink) !important;
}}

.st-key-filter-segment [data-testid="stMultiSelectTagsContainer"] [role="group"] > span > span,
.st-key-filter-country [data-testid="stMultiSelectTagsContainer"] [role="group"] > span > span {{
    background: transparent !important;
    border: 0 !important;
    color: var(--selection-ink) !important;
}}

.st-key-filter-segment [role="combobox"],
.st-key-filter-country [role="combobox"] {{
    color: var(--ink) !important;
}}

.st-key-filter-segment [role="combobox"]::placeholder,
.st-key-filter-country [role="combobox"]::placeholder {{
    color: var(--muted) !important;
    opacity: 1 !important;
}}

.st-key-filter-date [data-testid="stSliderThumbValue"] {{
    color: var(--orange) !important;
}}

.st-key-filter-date [data-testid="stSliderTickBar"] {{
    color: var(--muted) !important;
}}

.st-key-filter-date [data-testid="stSlider"] [style*="left:"][style*="%"] {{
    background-color: var(--orange) !important;
}}

.st-key-filter-date [data-testid="stSlider"] div[style*="position: relative"] > div:first-child {{
    filter: hue-rotate(165deg) saturate(0.7);
}}

div[data-baseweb="select"] > div:hover {{
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba({C['accent_rgb']}, 0.1) !important;
}}

div[data-baseweb="select"] > div:focus-within {{
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba({C['accent_rgb']}, 0.2) !important;
}}

.stMultiSelect [data-baseweb="tag"] {{
    background: var(--card-hover) !important;
    color: var(--orange) !important;
    border: 1px solid var(--line) !important;
}}

/* ===== INSIGHT CARDS ===== */
.insight-grid {{
    display: grid;
    grid-template-columns: 1.6fr repeat(4, 1fr);
    gap: 16px;
    margin: 0 0 32px;
    overflow: visible;
}}

.insight-card {{
    position: relative;
    min-height: 160px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 20px 20px 18px;
    box-shadow: 0 8px 24px rgba(32, 40, 49, 0.08);
    transition: all 0.25s ease;
    cursor: pointer;
    overflow: hidden;
}}

.insight-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba({C['accent_rgb']}, 0.15);
    border-color: var(--orange);
    background: var(--card-hover);
}}

.insight-card:hover > :not(.story) {{
    filter: blur(2px);
    opacity: 0.28;
}}

.insight-card.hero {{
    background: linear-gradient(135deg, {C['action']}, {C['action_light']});
    border-color: {C['action']};
    color: white;
}}

.insight-card.hero:hover {{
    box-shadow: 0 20px 50px rgba({C['accent_rgb']}, 0.4);
}}

.card-kicker {{
    color: var(--muted);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 700;
    margin: 0 0 8px 0;
}}

.insight-card.hero .card-kicker {{
    color: rgba(255, 255, 255, 0.8);
}}

.card-value {{
    color: var(--orange);
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    line-height: 1.05;
    margin: 8px 0 4px;
    font-weight: 600;
}}

.insight-card.hero .card-value {{
    color: white;
    font-size: 2.2rem;
}}

.card-label {{
    color: var(--ink);
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0;
}}

.insight-card.hero .card-label {{
    color: rgba(255, 255, 255, 0.95);
}}

.card-mini {{
    color: var(--muted);
    font-size: 0.7rem;
    line-height: 1.5;
    margin-top: 8px;
}}

.insight-card.hero .card-mini {{
    color: rgba(255, 255, 255, 0.75);
}}

/* Hover Story Tooltip */
.story {{
    position: absolute;
    inset: 0;
    z-index: 20;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: transparent;
    color: var(--ink);
    border: 0;
    border-radius: inherit;
    padding: 20px;
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    transform: translateY(4px);
    transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s ease;
    font-size: 0.75rem;
    line-height: 1.6;
    max-width: none;
}}

.insight-card:hover .story {{
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}}

.insight-card.hero .story-title,
.insight-card.hero .story-text {{
    color: white;
}}

.story-title {{
    color: var(--orange);
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    font-weight: 600;
    margin: 0 0 6px 0;
}}

.story-text {{
    color: var(--muted);
    margin: 0;
}}

/* ===== SECTIONS & CHARTS ===== */
.section-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 32px 0 16px;
}}

.section-label {{
    color: var(--orange);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 700;
    margin: 0;
}}

.section-hint {{
    color: var(--muted);
    font-size: 0.65rem;
}}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] [data-testid="stPlotlyChart"]) {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(32, 40, 49, 0.08);
    margin-bottom: 24px;
    transition: all 0.2s ease;
}}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] [data-testid="stPlotlyChart"]):hover {{
    border-color: var(--orange);
    box-shadow: 0 12px 32px rgba({C['accent_rgb']}, 0.1);
}}

.chart-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ink);
    margin: 0 0 16px 0;
}}

/* ===== SEGMENTS ===== */
.seg-row {{
    background: var(--card);
    border: 1px solid var(--line);
    border-left: 4px solid var(--seg-color);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    transition: all 0.2s ease;
}}

.seg-row:hover {{
    transform: translateX(4px);
    box-shadow: 0 12px 28px rgba(32, 40, 49, 0.08);
    border-color: var(--orange);
}}

.seg-name {{
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: var(--ink);
    margin: 0 0 6px 0;
    font-weight: 600;
}}

.seg-note {{
    color: var(--muted);
    font-size: 0.75rem;
    margin: 0 0 14px 0;
    line-height: 1.5;
}}

.metric-label {{
    color: var(--muted);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 4px 0;
}}

.metric-value {{
    color: var(--orange);
    font-size: 1rem;
    font-weight: 700;
    margin: 0;
}}

.pill {{
    display: inline-block;
    background: var(--card-hover);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 6px 12px;
    margin: 6px 6px 0 0;
    font-size: 0.65rem;
    color: var(--muted);
    transition: all 0.2s ease;
}}

.pill:hover {{
    background: var(--action);
    color: white;
    border-color: var(--action);
}}

.segment-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin: 8px 0 32px;
}}

.segment-card {{
    min-width: 0;
    padding: 20px;
    background: var(--card);
    border: 1px solid var(--line);
    border-top: 4px solid var(--segment-color);
    border-radius: 12px;
    box-shadow: 0 8px 22px rgba(32, 40, 49, 0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}}

.segment-card:hover {{
    transform: translateY(-3px);
    border-color: var(--segment-color);
    box-shadow: 0 14px 28px rgba(32, 40, 49, 0.12);
}}

.segment-header {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
}}

.segment-identity {{
    display: flex;
    align-items: center;
    gap: 9px;
    min-width: 0;
}}

.segment-dot {{
    flex: 0 0 10px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--segment-color);
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--segment-color) 16%, transparent);
}}

.segment-name {{
    margin: 0;
    color: var(--ink);
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    line-height: 1.25;
    font-weight: 600;
}}

.segment-customer-count {{
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
}}

.segment-customer-count strong {{
    color: var(--segment-color);
    font-size: 1.15rem;
    line-height: 1.1;
}}

.segment-customer-count span,
.segment-metric-label,
.segment-actions-label {{
    color: var(--muted);
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.segment-note {{
    min-height: 48px;
    margin: 10px 0 16px;
    color: var(--muted);
    font-size: 0.74rem;
    line-height: 1.5;
}}

.segment-metrics {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    padding-top: 14px;
    border-top: 1px solid var(--line);
}}

.segment-metric {{
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 5px;
}}

.segment-metric + .segment-metric {{
    padding-left: 12px;
    border-left: 1px solid var(--line);
}}

.segment-metric-value {{
    color: var(--segment-color);
    font-size: 1.12rem;
    font-weight: 700;
    line-height: 1.15;
    white-space: nowrap;
}}

.segment-actions {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-top: 15px;
    padding-top: 13px;
    border-top: 1px solid var(--line);
}}

.segment-actions-label {{
    flex: 0 0 100%;
    margin-bottom: 2px;
}}

.segment-action {{
    padding: 5px 8px;
    border: 1px solid var(--selection-border);
    border-radius: 999px;
    background: var(--selection-bg);
    color: var(--selection-ink);
    font-size: 0.64rem;
    line-height: 1.2;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 1250px) {{
    .insight-grid {{
        grid-template-columns: repeat(3, 1fr);
    }}
    .insight-card.hero {{
        grid-column: span 3;
    }}
    .segment-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
}}

@media (max-width: 850px) {{
    .block-container {{
        padding: 1rem;
    }}
    .insight-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    .insight-card.hero {{
        grid-column: span 2;
    }}
    .segment-grid {{
        grid-template-columns: 1fr;
    }}
    .filter-bar {{
        flex-direction: column;
    }}
    .filter-group {{
        width: 100%;
    }}
}}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data(show_spinner="Loading customer data...")
def load_data():
    tx = pd.read_csv("../streamlit/transactions_with_segments.csv")
    returns = pd.read_csv("../streamlit/returns_data.csv")
    guests = pd.read_csv("../streamlit/guests_data.csv")

    tx["InvoiceDate"] = pd.to_datetime(tx["InvoiceDate"], errors="coerce")
    returns["InvoiceDate"] = pd.to_datetime(returns["InvoiceDate"], errors="coerce")
    guests["InvoiceDate"] = pd.to_datetime(guests["InvoiceDate"], errors="coerce")

    return tx, returns, guests


try:
    tx, returns_df, guests_df = load_data()
except FileNotFoundError as e:
    st.error(
        f"Missing data file: {e.filename}.\n\n"
        "Keep these three files in the SAME folder as app.py:\n"
        "• transactions_with_segments.csv\n"
        "• returns_data.csv\n"
        "• guests_data.csv"
    )
    st.stop()

tx = tx.dropna(subset=["InvoiceDate"]).copy()

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
nav_items = [
    "📊 Overview",
    "👥 Customer Segments",
    "📦 Products & Markets",
    "🎯 Strategy & Actions",
    "🔄 Guests & Returns",
]

with st.sidebar:
    st.markdown(
        '<div class="brand">'
        '<div class="brand-icon">◈</div>'
        '<div><div class="brand-title">Customer<br>Intel</div>'
        '<div class="brand-sub">RFM · SEGMENTATION</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-label">Navigate</div>', unsafe_allow_html=True)
    selected = st.radio("Navigation", nav_items, index=0, label_visibility="collapsed")
    page = selected.split(" ", 1)[1]

    st.markdown(
        '<div class="sidebar-help">'
        '<div class="sidebar-help-title">💡 How to use</div>'
        '<div class="sidebar-help-text">'
        'Hover on any insight card to see the business story. Hover on chart points for detailed context. '
        'Use filters to update all visuals.'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-foot">Customer Segmentation · Online Retail</div>', unsafe_allow_html=True)


# =============================================================================
# HEADER + FILTERS
# =============================================================================
title_column, theme_column = st.columns([1, 0.08], vertical_alignment="center")
with title_column:
    st.markdown(
        '<div class="header">'
        '<div><div class="page-title">Customer Intelligence</div>'
        '<div class="page-subtitle">Online Retail · RFM Segmentation & Marketing Playbook</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
with theme_column:
    st.button(
        "☀" if dark_mode else "☾",
        key="theme-toggle",
        help="Switch to light theme" if dark_mode else "Switch to dark theme",
        on_click=toggle_theme,
    )
st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns([1.2, 1.5, 1.3])

with f1:
    with st.container(border=True, key="filter-segment"):
        st.markdown('<div class="filter-label">Segment</div>', unsafe_allow_html=True)
        segment_options = sorted(tx["Segment_Name"].dropna().unique().tolist())
        segments = st.multiselect(
            "Segment",
            segment_options,
            default=segment_options,
            label_visibility="collapsed",
        )

with f2:
    with st.container(border=True, key="filter-country"):
        st.markdown('<div class="filter-label">Country</div>', unsafe_allow_html=True)
        country_options = sorted(tx["Country"].dropna().unique().tolist())
        selected_countries = st.multiselect(
            "Country",
            country_options,
            default=[],
            placeholder="All Countries",
            label_visibility="collapsed",
        )

with f3:
    with st.container(border=True, key="filter-date"):
        st.markdown('<div class="filter-label">Date Range</div>', unsafe_allow_html=True)
        min_d = tx["InvoiceDate"].min().date()
        max_d = tx["InvoiceDate"].max().date()
        date_range = st.slider(
            "Date range",
            min_value=min_d,
            max_value=max_d,
            value=(min_d, max_d),
            label_visibility="collapsed",
        )

# Apply filters
country_mask = (
    tx["Country"].isin(selected_countries)
    if selected_countries
    else pd.Series(True, index=tx.index)
)

mask = (
    tx["Segment_Name"].isin(segments)
    & country_mask
    & tx["InvoiceDate"].dt.date.ge(date_range[0])
    & tx["InvoiceDate"].dt.date.le(date_range[1])
)
ftx = tx.loc[mask].copy()

if ftx.empty:
    st.warning("No transactions match these filters. Try adjusting your selection.")
    st.stop()


# =============================================================================
# AGGREGATIONS
# =============================================================================
per_cust = (
    ftx.groupby(["Segment_Name", "CustomerID"], dropna=True)
    .agg(
        last_purchase=("InvoiceDate", "max"),
        n_orders=("InvoiceNo", "nunique"),
        spend=("TransactionAmount", "sum"),
        items=("Quantity", "sum"),
    )
    .reset_index()
)

ref_date = tx["InvoiceDate"].max() + pd.Timedelta(days=1)
per_cust["recency_days"] = (ref_date - per_cust["last_purchase"]).dt.days

seg_summary = (
    per_cust.groupby("Segment_Name")
    .agg(
        Customers=("CustomerID", "nunique"),
        Recency=("recency_days", "mean"),
        Frequency=("n_orders", "mean"),
        Monetary=("spend", "sum"),
    )
    .reset_index()
)

if not seg_summary.empty and seg_summary["Monetary"].sum() != 0:
    seg_summary["Revenue_Pct"] = seg_summary["Monetary"] / seg_summary["Monetary"].sum() * 100
else:
    seg_summary["Revenue_Pct"] = 0

seg_order = [s for s in ["Champions", "Loyal Customers", "At Risk"] if s in seg_summary["Segment_Name"].values]
seg_summary["Segment_Name"] = pd.Categorical(seg_summary["Segment_Name"], seg_order, ordered=True)
seg_summary = seg_summary.sort_values("Segment_Name")

total_revenue = ftx["TransactionAmount"].sum()
total_customers = ftx["CustomerID"].nunique()
total_orders = ftx["InvoiceNo"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0

customer_order_counts = per_cust.groupby("CustomerID")["n_orders"].sum()
repeat_rate = float((customer_order_counts > 1).mean() * 100) if len(customer_order_counts) else 0

country_summary = (
    ftx.groupby("Country")["TransactionAmount"]
    .sum()
    .reset_index(name="Revenue")
    .sort_values("Revenue", ascending=False)
)
country_summary["Pct"] = country_summary["Revenue"] / country_summary["Revenue"].sum() * 100

top_country = country_summary.iloc[0]["Country"] if len(country_summary) else "—"
top_country_pct = float(country_summary.iloc[0]["Pct"]) if len(country_summary) else 0

product_summary = (
    ftx.groupby("Description")
    .agg(Revenue=("TransactionAmount", "sum"), Quantity=("Quantity", "sum"), Orders=("InvoiceNo", "nunique"))
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

top_products = product_summary.head(10)

monthly = (
    ftx.set_index("InvoiceDate")["TransactionAmount"]
    .resample("MS")
    .sum()
    .reset_index(name="Revenue")
)
monthly["Month"] = monthly["InvoiceDate"].dt.strftime("%b %Y")

champ = seg_summary[seg_summary["Segment_Name"] == "Champions"]
champ_revenue_pct = float(champ["Revenue_Pct"].iloc[0]) if len(champ) else 0
champ_customers = int(champ["Customers"].iloc[0]) if len(champ) else 0


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def money(v):
    return f"£{v:,.0f}"


def make_card(kicker, value, label, mini, story_title, story, hero=False):
    cls = "insight-card hero" if hero else "insight-card"
    return (
        f'<div class="{cls}">'
        f'<div class="card-kicker">{kicker}</div>'
        f'<div class="card-value">{value}</div>'
        f'<div class="card-label">{label}</div>'
        f'<div class="card-mini">{mini}</div>'
        f'<div class="story"><div class="story-title">{story_title}</div><p class="story-text">{story}</p></div>'
        f'</div>'
    )


def render_cards(card_list):
    html = '<div class="insight-grid">' + ''.join(card_list) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def section(title, hint=""):
    st.markdown(
        f'<div class="section-head"><p class="section-label">{title}</p>'
        f'<span class="section-hint">{hint}</span></div>',
        unsafe_allow_html=True,
    )


def chart_box(fig, height=380):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=16, t=20, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CHART_COLORWAY,
        font=dict(family="DM Sans", color=C["ink"], size=11),
        title_font=dict(family="Playfair Display", size=14, color=C["ink"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)", bordercolor=C["line"], borderwidth=1, font=dict(color=C["ink"])),
        hoverlabel=dict(bgcolor=C["card"], font_color=C["ink"], bordercolor=C["orange"]),
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor=C["line"],
        tickfont=dict(color=C["muted"]),
        title_font=dict(color=C["muted"]),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=C["line"],
        gridwidth=1,
        zeroline=False,
        tickfont=dict(color=C["muted"]),
        title_font=dict(color=C["muted"]),
    )
    with st.container(border=True):
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# =============================================================================
# PAGE 1 — OVERVIEW
# =============================================================================
if page == "Overview":
    render_cards([
        make_card(
            "TOTAL REVENUE",
            money(total_revenue),
            "Filtered revenue",
            f"{total_orders:,} orders · {total_customers:,} customers",
            "Revenue Baseline",
            f"The selected population generates {money(total_revenue)} from {total_orders:,} orders. This is your commercial baseline for all trends below.",
            hero=True,
        ),
        make_card(
            "AVERAGE BASKET",
            money(avg_order_value),
            "Average order value",
            "Revenue ÷ unique orders",
            "Basket Insight",
            "AOV is a key lever for growth. Track this metric to measure the effectiveness of upsell and bundling strategies.",
        ),
        make_card(
            "CHAMPIONS",
            f"{champ_revenue_pct:.1f}%",
            "Revenue share",
            f"{champ_customers:,} customers",
            "Value Concentration",
            f"Champions represent {champ_revenue_pct:.1f}% of revenue. This concentration shows why protecting this segment is critical.",
        ),
        make_card(
            "TOP MARKET",
            f"{top_country_pct:.1f}%",
            top_country,
            "Share of filtered revenue",
            "Market Story",
            f"{top_country} is your largest market at {top_country_pct:.1f}%. Use this as your primary market for initial campaigns.",
        ),
        make_card(
            "REPEAT BUYERS",
            f"{repeat_rate:.1f}%",
            "Customers with 2+ orders",
            "Selected customer population",
            "Retention Signal",
            "Repeat buyers demonstrate loyalty. This metric helps identify your core customer base vs first-time buyers.",
        ),
    ])

    a, b = st.columns([1.5, 1])
    with a:
        section("Revenue Trajectory", "Click points to see monthly revenue · Last 12 months")
        fig = go.Figure(go.Scatter(
            x=monthly["InvoiceDate"],
            y=monthly["Revenue"],
            mode="lines+markers",
            line=dict(color=C["orange"], width=3),
            marker=dict(size=8, color=C["orange"]),
            customdata=monthly[["Month", "Revenue"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Revenue: £%{customdata[1]:,.0f}<extra></extra>",
            fill="tozeroy",
            fillcolor=color_rgba(C["orange"], 0.08),
        ))
        if len(monthly):
            peak = monthly.loc[monthly["Revenue"].idxmax()]
            fig.add_annotation(
                x=peak["InvoiceDate"],
                y=peak["Revenue"],
                text="PEAK",
                showarrow=True,
                arrowhead=0,
                font=dict(color=C["orange"], size=10),
            )
        chart_box(fig, 380)

    with b:
        section("Top 10 Markets", "Revenue share · Hover for details")
        top10 = country_summary.head(10).sort_values("Pct")
        fig = go.Figure(go.Bar(
            x=top10["Pct"],
            y=top10["Country"],
            orientation="h",
            marker_color=C["blue"],
            customdata=top10[["Revenue"]],
            hovertemplate="<b>%{y}</b><br>Share: %{x:.1f}%<br>Revenue: £%{customdata[0]:,.0f}<extra></extra>",
        ))
        fig.update_layout(xaxis_title="Revenue share (%)")
        chart_box(fig, 380)

    a, b = st.columns(2)
    with a:
        section("Customer Value Curve", "Pareto principle · How concentrated revenue is")
        ranked = per_cust.sort_values("spend", ascending=False).reset_index(drop=True)
        ranked["cum_share"] = ranked["spend"].cumsum() / ranked["spend"].sum() * 100
        ranked["customer_pct"] = (ranked.index + 1) / len(ranked) * 100
        fig = go.Figure(go.Scatter(
            x=ranked["customer_pct"],
            y=ranked["cum_share"],
            mode="lines",
            line=dict(color=C["gold"], width=3),
            fill="tozeroy",
            fillcolor=color_rgba(C["gold"], 0.1),
            hovertemplate="Top %{x:.0f}% of customers<br>Cumulative revenue: %{y:.1f}%<extra></extra>",
        ))
        fig.update_layout(xaxis_title="Customers (% of total)", yaxis_title="Cumulative revenue (%)")
        chart_box(fig, 360)

    with b:
        section("Order Value Distribution", "Log-spaced value bins · Orders by value range")
        order_values = ftx.groupby("InvoiceNo")["TransactionAmount"].sum()
        order_values = order_values[order_values > 0]
        if order_values.empty:
            st.info("No positive order values for these filters.")
        else:
            log_values = order_values.map(math.log10)
            minimum_log = float(log_values.min())
            maximum_log = float(log_values.max())
            lower_decade = math.floor(minimum_log)
            upper_decade = math.ceil(maximum_log)
            if lower_decade == upper_decade:
                upper_decade += 1

            bin_count = 25
            bin_step = (upper_decade - lower_decade) / bin_count
            bin_edges = [lower_decade + index * bin_step for index in range(bin_count + 1)]
            binned_values = pd.cut(log_values, bins=bin_edges, include_lowest=True)
            order_counts = binned_values.value_counts(sort=False).tolist()
            bin_centers = [
                (bin_edges[index] + bin_edges[index + 1]) / 2
                for index in range(bin_count)
            ]
            bin_ranges = [
                [10 ** bin_edges[index], 10 ** bin_edges[index + 1]]
                for index in range(bin_count)
            ]
            tick_values = [
                exponent
                for exponent in range(lower_decade, upper_decade + 1)
                if minimum_log <= exponent <= maximum_log
            ]
            if not tick_values:
                tick_values = [(minimum_log + maximum_log) / 2]
            tick_labels = []
            for exponent in tick_values:
                tick_value = 10 ** exponent
                if tick_value < 1:
                    tick_labels.append(f"£{tick_value:g}")
                elif tick_value < 1000:
                    tick_labels.append(f"£{tick_value:,.0f}")
                else:
                    tick_labels.append(f"£{tick_value / 1000:g}k")

            fig = go.Figure(go.Bar(
                x=bin_centers,
                y=order_counts,
                width=bin_step,
                customdata=bin_ranges,
                marker_color=C["teal"],
                hovertemplate="Order value: £%{customdata[0]:,.0f} to £%{customdata[1]:,.0f}<br>Orders: %{y:,}<extra></extra>",
            ))
            fig.update_layout(
                xaxis_title="Order value (£, log scale)",
                yaxis_title="Orders",
                bargap=0.08,
            )
            fig.update_xaxes(
                range=[lower_decade, upper_decade],
                tickmode="array",
                tickvals=tick_values,
                ticktext=tick_labels,
            )
            chart_box(fig, 360)


# =============================================================================
# PAGE 2 — CUSTOMER SEGMENTS
# =============================================================================
elif page == "Customer Segments":
    total_risk = int(seg_summary.loc[seg_summary["Segment_Name"] == "At Risk", "Customers"].sum())
    total_loyal = int(seg_summary.loc[seg_summary["Segment_Name"] == "Loyal Customers", "Customers"].sum())
    avg_recency = float(per_cust["recency_days"].mean()) if len(per_cust) else 0
    avg_frequency = float(per_cust["n_orders"].mean()) if len(per_cust) else 0

    render_cards([
        make_card(
            "CUSTOMERS",
            f"{total_customers:,}",
            "Selected customers",
            "Unique Customer IDs",
            "Population Context",
            "This is your active customer population. Segment size determines the impact of retention initiatives.",
            hero=True,
        ),
        make_card(
            "CHAMPIONS",
            f"{champ_customers:,}",
            "Customers",
            f"{champ_revenue_pct:.1f}% revenue share",
            "Champion Profile",
            "High frequency, high value, low recency. These are your most valuable customers—protect and grow this segment.",
        ),
        make_card(
            "AT RISK",
            f"{total_risk:,}",
            "Customers",
            "Longer purchase gap",
            "Reactivation Opportunity",
            "High recency indicates dormancy. These customers are ideal targets for win-back campaigns and personalized offers.",
        ),
        make_card(
            "AVG RECENCY",
            f"{avg_recency:.0f}d",
            "Days since purchase",
            "Lower = fresher demand",
            "Freshness Metric",
            "Recency indicates purchase momentum. Lower values suggest active engagement; higher values suggest churn risk.",
        ),
        make_card(
            "AVG FREQUENCY",
            f"{avg_frequency:.1f}",
            "Orders per customer",
            "Across selected segments",
            "Loyalty Signal",
            "Frequency measures repeat purchasing. Combine with monetary value to identify loyal high-spenders vs occasional buyers.",
        ),
    ])

    section("Segment Details", "Segment profile · Performance · Recommended actions")
    segment_cards = []
    for _, row in seg_summary.iterrows():
        name = str(row["Segment_Name"])
        color = SEGMENT_COLOR.get(name, C["blue"])
        actions = "".join(
            f'<span class="segment-action">{action}</span>'
            for action in SEGMENT_ACTIONS.get(name, [])
        )
        segment_cards.append(
            f'<article class="segment-card" style="--segment-color:{color};">'
            f'<div class="segment-header">'
            f'<div class="segment-identity"><span class="segment-dot"></span>'
            f'<h3 class="segment-name">{name}</h3></div>'
            f'<div class="segment-customer-count"><strong>{int(row["Customers"]):,}</strong>'
            f'<span>customers</span></div></div>'
            f'<p class="segment-note">{SEGMENT_NOTE.get(name, "")}</p>'
            f'<div class="segment-metrics">'
            f'<div class="segment-metric"><span class="segment-metric-label">Avg recency</span>'
            f'<strong class="segment-metric-value">{row["Recency"]:.0f}d</strong></div>'
            f'<div class="segment-metric"><span class="segment-metric-label">Frequency</span>'
            f'<strong class="segment-metric-value">{row["Frequency"]:.1f}</strong></div>'
            f'<div class="segment-metric"><span class="segment-metric-label">Revenue</span>'
            f'<strong class="segment-metric-value">{row["Revenue_Pct"]:.1f}%</strong></div></div>'
            f'<div class="segment-actions"><span class="segment-actions-label">Recommended actions</span>'
            f'{actions}</div></article>'
        )
    segment_cards_html = "".join(segment_cards)
    st.markdown(
        f'<div class="segment-grid">{segment_cards_html}</div>',
        unsafe_allow_html=True,
    )

    a, b = st.columns(2)
    with a:
        section("Recency vs Spend", "Bubble size = order frequency · Hover for details")
        sample = per_cust.sample(min(1500, len(per_cust)), random_state=7) if len(per_cust) > 1500 else per_cust
        fig = px.scatter(
            sample,
            x="recency_days",
            y="spend",
            color="Segment_Name",
            size="n_orders",
            size_max=18,
            opacity=0.75,
            color_discrete_map=SEGMENT_COLOR,
            custom_data=["CustomerID", "n_orders"],
            labels={"recency_days": "Recency (days)", "spend": "Customer Spend (£)"},
        )
        fig.update_traces(
            hovertemplate="Customer: %{customdata[0]}<br>Recency: %{x:.0f}d<br>Spend: £%{y:,.0f}<br>Orders: %{customdata[1]}<extra></extra>"
        )
        fig.update_yaxes(type="log")
        chart_box(fig, 380)

    with b:
        section("Revenue Contribution", "Treemap by segment")
        fig = go.Figure(go.Treemap(
            labels=seg_summary["Segment_Name"].astype(str),
            parents=[""] * len(seg_summary),
            values=seg_summary["Monetary"],
            marker_colors=[SEGMENT_COLOR.get(str(s), C["blue"]) for s in seg_summary["Segment_Name"]],
            customdata=seg_summary[["Customers", "Revenue_Pct"]],
            texttemplate="<b>%{label}</b><br>£%{value:,.0f}<br>%{percentRoot:.1%}",
            hovertemplate="<b>%{label}</b><br>Revenue: £%{value:,.0f}<br>Customers: %{customdata[0]:,}<br>Share: %{customdata[1]:.1f}%<extra></extra>",
        ))
        chart_box(fig, 380)

    a, b = st.columns(2)
    with a:
        section("Segment Size", "Customer count by segment")
        fig = px.bar(
            seg_summary,
            x="Segment_Name",
            y="Customers",
            color="Segment_Name",
            color_discrete_map=SEGMENT_COLOR,
        )
        fig.update_traces(hovertemplate="%{x}<br>Customers: %{y:,}<extra></extra>")
        chart_box(fig, 360)

    with b:
        section("Purchase Frequency", "Average orders per customer")
        fig = px.bar(
            seg_summary,
            x="Segment_Name",
            y="Frequency",
            color="Segment_Name",
            color_discrete_map=SEGMENT_COLOR,
        )
        fig.update_traces(hovertemplate="%{x}<br>Avg Orders: %{y:.2f}<extra></extra>")
        fig.update_layout(yaxis_title="Orders per customer")
        chart_box(fig, 360)


# =============================================================================
# PAGE 3 — PRODUCTS & MARKETS
# =============================================================================
elif page == "Products & Markets":
    top_product_name = str(top_products.iloc[0]["Description"]) if len(top_products) else "—"
    top_product_revenue = float(top_products.iloc[0]["Revenue"]) if len(top_products) else 0
    market_count = country_summary["Country"].nunique()
    product_count = product_summary["Description"].nunique()
    return_rate = len(returns_df) / (len(returns_df) + len(ftx)) * 100 if returns_df is not None else 0

    render_cards([
        make_card(
            "TOP PRODUCT",
            money(top_product_revenue),
            top_product_name[:30],
            "Highest product revenue",
            "Hero Product",
            f"{top_product_name} is your revenue leader. Use this as a flagship for promotions and bundling strategies.",
            hero=True,
        ),
        make_card(
            "MARKETS",
            f"{market_count}",
            "Countries represented",
            "Geographic diversity",
            "Market Breadth",
            "Multiple markets reduce risk. Compare domestic vs. international revenue to prioritize expansion efforts.",
        ),
        make_card(
            "PRODUCTS",
            f"{product_count:,}",
            "Unique products",
            "SKUs in filtered data",
            "Assortment",
            "A large assortment enables cross-sell. But focus on top 20% of products that drive 80% of revenue.",
        ),
        make_card(
            "TOP MARKET",
            f"{top_country_pct:.1f}%",
            top_country,
            "Revenue concentration",
            "Market Focus",
            f"{top_country} dominates your revenue. Consider this your core market for customer acquisition.",
        ),
        make_card(
            "RETURN RATE",
            f"{return_rate:.2f}%",
            "Return lines vs transactions",
            f"{len(returns_df):,} return records",
            "Quality Signal",
            "High return rates can indicate product-market fit issues. Monitor by product and market to identify problem areas.",
        ),
    ])

    a, b = st.columns([1.4, 1])
    with a:
        section("Top 10 Products", "Revenue leaders · Hover for quantity and orders")
        top_p = top_products.sort_values("Revenue", ascending=True)
        fig = go.Figure(go.Bar(
            x=top_p["Revenue"],
            y=top_p["Description"],
            orientation="h",
            marker_color=C["orange"],
            customdata=top_p[["Quantity", "Orders"]],
            hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<br>Qty: %{customdata[0]:,.0f}<br>Orders: %{customdata[1]:,}<extra></extra>",
        ))
        chart_box(fig, 430)

    with b:
        section("Market Concentration", "Top 12 countries by revenue")
        top_m = country_summary.head(12).sort_values("Pct")
        fig = go.Figure(go.Bar(
            x=top_m["Pct"],
            y=top_m["Country"],
            orientation="h",
            marker_color=C["gold"],
            customdata=top_m[["Revenue"]],
            hovertemplate="<b>%{y}</b><br>Share: %{x:.1f}%<br>Revenue: £%{customdata[0]:,.0f}<extra></extra>",
        ))
        chart_box(fig, 430)

    a, b = st.columns(2)
    with a:
        section("Quantity vs Revenue", "Top 30 products · Bubble size = orders")
        scatter_products = product_summary.head(30)
        fig = px.scatter(
            scatter_products,
            x="Quantity",
            y="Revenue",
            size="Orders",
            hover_name="Description",
            size_max=25,
        )
        fig.update_traces(
            marker_color=C["blue"],
            hovertemplate="<b>%{hovertext}</b><br>Qty: %{x:,.0f}<br>Revenue: £%{y:,.0f}<extra></extra>",
        )
        chart_box(fig, 360)

    with b:
        section("Revenue Trend by Top Markets", "Top 5 countries · Monthly view")
        top5 = country_summary.head(5)["Country"].tolist()
        market_month = (
            ftx[ftx["Country"].isin(top5)]
            .assign(Month=ftx["InvoiceDate"].dt.to_period("M").astype(str))
            .groupby(["Month", "Country"])["TransactionAmount"]
            .sum()
            .reset_index(name="Revenue")
        )
        fig = px.line(
            market_month,
            x="Month",
            y="Revenue",
            color="Country",
            markers=True,
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig.update_traces(
            hovertemplate="%{fullData.name}<br>%{x}<br>Revenue: £%{y:,.0f}<extra></extra>"
        )
        chart_box(fig, 360)


# =============================================================================
# PAGE 4 — STRATEGY & ACTIONS
# =============================================================================
elif page == "Strategy & Actions":
    at_risk = seg_summary[seg_summary["Segment_Name"] == "At Risk"]
    total_risk = int(at_risk["Customers"].sum())
    risk_pct = float(at_risk["Revenue_Pct"].iloc[0]) if len(at_risk) else 0
    loyal = seg_summary[seg_summary["Segment_Name"] == "Loyal Customers"]
    loyal_pct = float(loyal["Revenue_Pct"].iloc[0]) if len(loyal) else 0

    render_cards([
        make_card(
            "PRIORITY",
            "Protect",
            "Champion retention",
            f"{champ_revenue_pct:.1f}% revenue share",
            "Strategic Focus",
            "Champions are disproportionately valuable. Every % of Champions you retain directly impacts revenue.",
            hero=True,
        ),
        make_card(
            "AT RISK",
            f"{risk_pct:.1f}%",
            "Revenue share",
            f"{total_risk:,} customers",
            "Win-Back Opportunity",
            "At Risk customers are the most cost-effective reactivation target. Time-sensitive outreach is critical.",
        ),
        make_card(
            "LOYAL",
            f"{loyal_pct:.1f}%",
            "Revenue share",
            "Core recurring demand",
            "Growth Lever",
            "Loyal Customers bridge current revenue and future Champions. Cross-sell and upsell drive this transition.",
        ),
        make_card(
            "TOP MARKET",
            top_country,
            "Primary focus",
            f"{top_country_pct:.1f}% of revenue",
            "Geographic Priority",
            f"Concentrate segment-specific campaigns in {top_country} before scaling internationally.",
        ),
        make_card(
            "PLAYBOOK",
            "3",
            "Core actions",
            "Protect · Grow · Reactivate",
            "Execution Model",
            "Each segment gets a tailored action. Apply the playbook consistently for measurable results.",
        ),
    ])

    section("Segment Playbook", "Action layer built on RFM segments")
    for _, row in seg_summary.iterrows():
        name = str(row["Segment_Name"])
        color = SEGMENT_COLOR.get(name, C["blue"])
        pills = "".join(f'<span class="pill">{a}</span>' for a in SEGMENT_ACTIONS.get(name, []))
        st.markdown(
            f'<div class="seg-row" style="--seg-color:{color};">'
            f'<div class="seg-name">{name} · {int(row["Customers"]):,} customers · {row["Revenue_Pct"]:.1f}% revenue</div>'
            f'<div class="seg-note">{SEGMENT_NOTE.get(name, "")}</div>{pills}</div>',
            unsafe_allow_html=True,
        )

    a, b = st.columns(2)
    with a:
        section("Revenue by Segment", "Share of total revenue")
        fig = px.bar(
            seg_summary,
            x="Segment_Name",
            y="Revenue_Pct",
            color="Segment_Name",
            color_discrete_map=SEGMENT_COLOR,
        )
        fig.update_traces(hovertemplate="%{x}<br>Share: %{y:.1f}%<extra></extra>")
        fig.update_layout(yaxis_title="Revenue share (%)")
        chart_box(fig, 360)

    with b:
        section("Customers vs Revenue", "Bubble size = avg frequency")
        fig = px.scatter(
            seg_summary,
            x="Customers",
            y="Monetary",
            size="Frequency",
            color="Segment_Name",
            color_discrete_map=SEGMENT_COLOR,
            text="Segment_Name",
        )
        fig.update_traces(
            textposition="top center",
            hovertemplate="%{text}<br>Customers: %{x:,}<br>Revenue: £%{y:,.0f}<extra></extra>",
        )
        chart_box(fig, 360)

    a, b = st.columns(2)
    with a:
        section("Recency by Segment", "Lower = more recent purchases")
        fig = px.bar(
            seg_summary,
            x="Segment_Name",
            y="Recency",
            color="Segment_Name",
            color_discrete_map=SEGMENT_COLOR,
        )
        fig.update_traces(hovertemplate="%{x}<br>Avg Recency: %{y:.0f}d<extra></extra>")
        fig.update_layout(yaxis_title="Recency (days)")
        chart_box(fig, 360)

    with b:
        section("Market Opportunity", "Top 10 markets by revenue")
        market = country_summary.head(10).sort_values("Revenue")
        fig = go.Figure(go.Bar(
            x=market["Revenue"],
            y=market["Country"],
            orientation="h",
            marker_color=C["blue"],
            customdata=market[["Pct"]],
            hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<br>Share: %{customdata[0]:.1f}%<extra></extra>",
        ))
        chart_box(fig, 360)

    st.download_button(
        "📥 Download Segment Summary (CSV)",
        seg_summary.to_csv(index=False).encode("utf-8"),
        file_name="segment_summary.csv",
        mime="text/csv",
    )


# =============================================================================
# PAGE 5 — GUESTS & RETURNS
# =============================================================================
else:
    guest_revenue = guests_df["TransactionAmount"].sum()
    guest_customers = guests_df["GuestID"].nunique()
    return_value = abs(returns_df["TransactionAmount"].sum())
    return_lines = len(returns_df)
    guest_share = guest_revenue / total_revenue * 100 if total_revenue else 0

    render_cards([
        make_card(
            "GUEST REVENUE",
            money(guest_revenue),
            "Unregistered customers",
            f"{guest_share:.1f}% of filtered revenue",
            "Anonymous Demand",
            "Guest revenue represents unidentified customers. Converting these to registered users unlocks segmentation potential.",
            hero=True,
        ),
        make_card(
            "GUEST BASKETS",
            f"{guest_customers:,}",
            "Guest IDs",
            f"{len(guests_df):,} transaction lines",
            "Guest Profile",
            "Multiple guest IDs indicate repeat unregistered behavior. Incentivize registration to move these to known customers.",
        ),
        make_card(
            "RETURN VALUE",
            money(return_value),
            "Value represented",
            f"{return_lines:,} return lines",
            "Returns Context",
            "Returns reduce net revenue. High return rates in specific products/markets signal quality or fit issues.",
        ),
        make_card(
            "RETURN LINES",
            f"{return_lines:,}",
            "Recorded returns",
            "From returns data",
            "Operational View",
            "Monitor return trends by product and market. Rising returns may indicate customer dissatisfaction.",
        ),
        make_card(
            "OPPORTUNITY",
            f"{guest_share:.1f}%",
            "Upside from conversion",
            "Guest revenue as % of total",
            "Conversion Potential",
            f"If you convert {guest_share:.1f}% of guest revenue into registered customers, you unlock {guest_share:.1f}% more segmentation insights.",
        ),
    ])

    a, b = st.columns(2)
    with a:
        section("Returns by Product", "Top 12 returned items")
        returned = returns_df.groupby("Description")["Quantity"].sum().abs().sort_values(ascending=False).head(12).sort_values()
        fig = go.Figure(go.Bar(
            x=returned.values,
            y=returned.index,
            orientation="h",
            marker_color=C["red"],
            hovertemplate="<b>%{y}</b><br>Qty Returned: %{x:,.0f}<extra></extra>",
        ))
        chart_box(fig, 400)

    with b:
        section("Guest Revenue by Country", "Top 12 guest markets")
        guest_country = guests_df.groupby("Country")["TransactionAmount"].sum().sort_values(ascending=False).head(12).sort_values()
        fig = go.Figure(go.Bar(
            x=guest_country.values,
            y=guest_country.index,
            orientation="h",
            marker_color=C["blue"],
            hovertemplate="<b>%{y}</b><br>Guest Revenue: £%{x:,.0f}<extra></extra>",
        ))
        chart_box(fig, 400)

    a, b = st.columns(2)
    with a:
        section("Guest Revenue Trend", "Monthly guest spending")
        guest_month = guests_df.set_index("InvoiceDate")["TransactionAmount"].resample("MS").sum().reset_index(name="Revenue")
        fig = go.Figure(go.Scatter(
            x=guest_month["InvoiceDate"],
            y=guest_month["Revenue"],
            mode="lines+markers",
            line=dict(color=C["teal"], width=3),
            marker=dict(size=7, color=C["teal"]),
            fill="tozeroy",
            fillcolor=color_rgba(C["teal"], 0.1),
            hovertemplate="%{x|%b %Y}<br>Guest Revenue: £%{y:,.0f}<extra></extra>",
        ))
        chart_box(fig, 360)

    with b:
        section("Return Value Trend", "Monthly returns impact")
        return_month = returns_df.set_index("InvoiceDate")["TransactionAmount"].resample("MS").sum().abs().reset_index(name="ReturnValue")
        fig = go.Figure(go.Scatter(
            x=return_month["InvoiceDate"],
            y=return_month["ReturnValue"],
            mode="lines+markers",
            line=dict(color=C["red"], width=3),
            marker=dict(size=7, color=C["red"]),
            fill="tozeroy",
            fillcolor=color_rgba(C["red"], 0.1),
            hovertemplate="%{x|%b %Y}<br>Return Value: £%{y:,.0f}<extra></extra>",
        ))
        chart_box(fig, 360)