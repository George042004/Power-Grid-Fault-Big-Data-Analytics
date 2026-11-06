"""
Header, KPI card and status pill components.
"""
import streamlit as st
from typing import Optional


def render_header(title: str, subtitle: Optional[str] = None):
    """Renders the page title with project ownership details."""
    sub = subtitle or "Power-grid fault analytics and real-time monitoring"
    st.markdown(f"""
    <div class="page-header">
        <div>
            <h1 class="page-title">{title}</h1>
            <div class="page-subtitle">{sub}</div>
        </div>
        <div class="owner-chip">
            <strong>Marumudi George Mullar</strong><br>
            Guide: Mr. R. SriRamu
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, subtext: str = "", border_color: str = "#0B7A75"):
    """Renders a KPI card; the left stripe colour carries meaning (e.g. red for critical)."""
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {border_color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_pill(status: str) -> str:
    """Returns HTML for an operating status pill."""
    st_upper = status.upper()
    if st_upper in ["NORMAL", "OPERATIONAL", "RUNNING"]:
        cls = "status-normal"
    elif st_upper == "WARNING":
        cls = "status-warning"
    else:
        cls = "status-critical"
    return f'<span class="status-pill {cls}">{status.capitalize()}</span>'
