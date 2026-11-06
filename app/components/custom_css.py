"""
Light operations-dashboard styling for Streamlit.

Palette
- Page      #F3F5F7   Panel   #FFFFFF   Line  #DDE3E8
- Ink       #14212B   Muted   #5B6B78
- Sidebar   #0F2230   Accent  #0B7A75 (teal)
- Status    ok #1F9D63 | warning #D98A00 | critical #D1362F
"""
import streamlit as st


def inject_custom_css():
    """Injects the dashboard stylesheet into the Streamlit DOM."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

        :root {
            --page: #F3F5F7;
            --panel: #FFFFFF;
            --line: #DDE3E8;
            --ink: #14212B;
            --muted: #5B6B78;
            --accent: #0B7A75;
            --ok: #1F9D63;
            --warn: #D98A00;
            --crit: #D1362F;
            --sidebar: #0F2230;
        }

        html, body, .stApp, [class*="css"] {
            font-family: 'IBM Plex Sans', 'Segoe UI', -apple-system, Roboto, sans-serif;
            font-variant-numeric: tabular-nums;
        }
        .stApp { background-color: var(--page); color: var(--ink); }
        .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }
        header[data-testid="stHeader"] { background: transparent; }

        h2, h3, [data-testid="stHeading"] h3 {
            color: var(--ink);
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        hr { border: none; border-top: 1px solid var(--line); margin: 1.8rem 0; }

        /* ---------- Page header ---------- */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 24px;
            padding-bottom: 16px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--line);
        }
        .page-title {
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--ink);
            margin: 0;
            line-height: 1.2;
        }
        .page-subtitle { font-size: 0.95rem; color: var(--muted); margin-top: 6px; }
        .owner-chip {
            font-size: 0.8rem;
            color: var(--muted);
            text-align: right;
            line-height: 1.5;
            white-space: nowrap;
        }
        .owner-chip strong { color: var(--ink); font-weight: 600; }

        /* ---------- KPI cards ---------- */
        .kpi-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent);
            border-radius: 6px;
            padding: 14px 18px 12px 18px;
            height: 100%;
        }
        .kpi-label { font-size: 0.85rem; color: var(--muted); margin-bottom: 4px; }
        .kpi-value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--ink);
            line-height: 1.15;
            letter-spacing: -0.02em;
        }
        .kpi-subtext { font-size: 0.78rem; color: var(--muted); margin-top: 4px; }

        /* ---------- Status pills ---------- */
        .status-pill {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            border: 1px solid transparent;
        }
        .status-normal   { background: #E6F5EE; color: #17754A; border-color: #BFE3D0; }
        .status-warning  { background: #FDF1D8; color: #8F5C00; border-color: #F1D79B; }
        .status-critical { background: #FBE5E3; color: #A5231D; border-color: #F0BDB9; }

        /* ---------- Alert rows ---------- */
        .alert-row {
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--warn);
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }
        .alert-row.critical { border-left-color: var(--crit); }
        .alert-row.normal   { border-left-color: var(--ok); }
        .alert-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 6px;
        }
        .alert-title { font-weight: 600; font-size: 1rem; color: var(--ink); }
        .alert-meta  { font-size: 0.8rem; color: var(--muted); white-space: nowrap; }
        .alert-line  { font-size: 0.86rem; color: var(--ink); margin-top: 3px; line-height: 1.45; }
        .alert-line span { color: var(--muted); }

        /* ---------- Station cards ---------- */
        .station-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-top: 4px solid var(--ok);
            border-radius: 6px;
            padding: 12px 14px;
            height: 100%;
        }
        .station-card.warning  { border-top-color: var(--warn); }
        .station-card.critical { border-top-color: var(--crit); }
        .station-id   { font-weight: 700; font-size: 1rem; color: var(--ink); }
        .station-name { font-size: 0.84rem; color: var(--ink); margin: 2px 0 8px 0; min-height: 2.4em; }
        .station-meta { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }
        .station-card .status-pill { margin-top: 10px; }

        /* ---------- Sidebar ---------- */
        div[data-testid="stSidebar"] { background-color: var(--sidebar); }
        div[data-testid="stSidebar"] * { color: #D5E0E8; }
        .brand-block { padding: 6px 4px 14px 4px; border-bottom: 1px solid #243B4C; margin-bottom: 14px; }
        .brand-name { font-size: 1.15rem; font-weight: 700; color: #FFFFFF !important; letter-spacing: -0.01em; }
        .brand-sub  { font-size: 0.8rem; color: #8FA6B6 !important; margin-top: 2px; }
        div[data-testid="stSidebar"] div[role="radiogroup"] { gap: 2px; }
        div[data-testid="stSidebar"] div[role="radiogroup"] label {
            padding: 7px 10px;
            border-radius: 6px;
            width: 100%;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: #17313F; }
        div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: #1B3B4C;
            box-shadow: inset 3px 0 0 #3CC4BC;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none; }
        div[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: 0.8rem; color: #8FA6B6 !important; }
        .sidebar-foot { font-size: 0.78rem; color: #8FA6B6 !important; line-height: 1.6; padding: 4px; }
        .sidebar-foot strong { color: #D5E0E8 !important; font-weight: 600; }

        /* ---------- Controls ---------- */
        div.stButton > button {
            background: var(--panel);
            color: var(--ink);
            border: 1px solid #B8C4CD;
            border-radius: 6px;
            font-weight: 600;
        }
        div.stButton > button:hover { border-color: var(--accent); color: var(--accent); }
        div.stButton > button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 6px; }
        div[data-testid="stPlotlyChart"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 6px;
            padding: 6px;
        }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 6px;
            padding: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
