"""
Alert rows for the fault feed.
"""
import streamlit as st
from typing import Dict, Any


def render_alert_banner(fault: Dict[str, Any]):
    """Renders one fault incident as a compact row with a severity stripe."""
    severity = fault.get("severity", "WARNING").upper()
    cls_name = "critical" if severity == "CRITICAL" else ("normal" if severity == "NORMAL" else "warning")
    pill_cls = {"critical": "status-critical", "normal": "status-normal", "warning": "status-warning"}[cls_name]
    fault_type = fault.get("predicted_fault") or fault.get("fault_type", "Fault detected")
    path = fault.get("localization_path", "Grid node")
    action = fault.get("recommended_action", "Inspect station")
    conf = fault.get("confidence", 0.95)

    st.markdown(f"""
    <div class="alert-row {cls_name}">
        <div class="alert-top">
            <div class="alert-title">{fault_type}
                <span class="status-pill {pill_cls}" style="margin-left:8px;">{severity.capitalize()}</span>
            </div>
            <div class="alert-meta">Confidence {conf * 100:.1f}%</div>
        </div>
        <div class="alert-line"><span>Location</span>&nbsp; {path}</div>
        <div class="alert-line"><span>Action</span>&nbsp; {action}</div>
    </div>
    """, unsafe_allow_html=True)
