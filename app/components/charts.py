"""
Plotly visualization builders styled with control-room dark theme.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Theme Palette
BG_COLOR = "#FFFFFF"
PAPER_BG = "#FFFFFF"
GRID_COLOR = "#E6EBEF"
TEXT_COLOR = "#14212B"
MUTED = "#5B6B78"
CYAN = "#0B7A75"      # primary accent (teal)
GREEN = "#1F9D63"
AMBER = "#D98A00"
RED = "#D1362F"
PURPLE = "#6D5BD0"


def plot_health_gauge(score: float) -> go.Figure:
    """Renders circular radial gauge for overall grid health."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Grid health", "font": {"size": 14, "color": MUTED}},
        number={"suffix": "%", "font": {"size": 30, "color": TEXT_COLOR}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": GRID_COLOR},
            "bar": {"color": CYAN},
            "bgcolor": "#FFFFFF",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60], "color": "rgba(209, 54, 47, 0.22)"},
                {"range": [60, 85], "color": "rgba(217, 138, 0, 0.22)"},
                {"range": [85, 100], "color": "rgba(31, 157, 99, 0.22)"}
            ],
            "threshold": {
                "line": {"color": TEXT_COLOR, "width": 3},
                "thickness": 0.8,
                "value": score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT_COLOR},
        height=280,
        margin=dict(l=30, r=30, t=50, b=30)
    )
    return fig


def plot_fault_donut(distribution_data: List[Dict[str, Any]]) -> go.Figure:
    """Renders donut chart for fault distribution."""
    if not distribution_data:
        df = pd.DataFrame([{"fault_type": "No Data", "count": 1}])
    else:
        df = pd.DataFrame(distribution_data)

    color_map = {
        "Normal": GREEN,
        "Overload": AMBER,
        "Short Circuit": RED,
        "Voltage Sag": "#3A8FD6",
        "Voltage Swell": "#6D5BD0",
        "Frequency Anomaly": PURPLE,
        "Overheating": "#E0603F",
        "No Data": "#9AA8B4"
    }

    colors = [color_map.get(f, CYAN) for f in df["fault_type"]]

    fig = go.Figure(data=[go.Pie(
        labels=df["fault_type"],
        values=df["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent",
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT_COLOR, "size": 11},
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=11)),
        height=300,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig


def plot_telemetry_line(df: pd.DataFrame, y_col: str, title: str, unit: str, color: str = CYAN, nominal: Optional[float] = None) -> go.Figure:
    """Renders real-time telemetry parameter timeline."""
    fig = go.Figure()

    if not df.empty and y_col in df.columns:
        df = df.sort_values("timestamp")
        multi = "station_id" in df.columns and df["station_id"].nunique() > 1
        if multi:
            palette = ["#0B7A75", "#3A8FD6", "#D98A00", "#6D5BD0", "#D1362F", "#1F9D63"]
            for i, (sid, g) in enumerate(df.groupby("station_id")):
                fig.add_trace(go.Scatter(
                    x=g["timestamp"], y=g[y_col], mode="lines+markers", name=str(sid),
                    line=dict(color=palette[i % len(palette)], width=1.8),
                    marker=dict(size=3), hoverinfo="x+y+name"
                ))
        else:
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df[y_col],
                mode="lines+markers",
                name=f"{title} ({unit})",
                line=dict(color=color, width=2),
                marker=dict(size=3),
                hoverinfo="x+y"
            ))

        if nominal is not None:
            fig.add_hline(
                y=nominal,
                line_dash="dot",
                line_color="#8493A0",
                annotation_text=f"Nominal ({nominal} {unit})",
                annotation_position="bottom right"
            )

    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT_COLOR, size=14)),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=10),
        height=240,
        showlegend=bool(not df.empty and "station_id" in df.columns and df["station_id"].nunique() > 1),
        legend=dict(orientation="h", y=1.18, x=1, xanchor="right", font=dict(size=10)),
        margin=dict(l=40, r=20, t=40, b=25),
        xaxis=dict(showgrid=False, showline=True, linecolor=GRID_COLOR),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, showline=False, title=unit)
    )
    return fig


def plot_confusion_matrix(cm: List[List[int]], classes: List[str]) -> go.Figure:
    """Plots interactive Confusion Matrix Heatmap."""
    cm_arr = np.array(cm)
    fig = go.Figure(data=go.Heatmap(
        z=cm_arr,
        x=classes,
        y=classes,
        colorscale=[[0, "#F3F7F8"], [1, "#0B7A75"]],
        hoverongaps=False,
        text=cm_arr,
        texttemplate="%{text}",
        textfont={"size": 12}
    ))
    fig.update_layout(
        title="Confusion matrix",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        xaxis_title="Predicted class",
        yaxis_title="True class",
        height=450,
        margin=dict(l=80, r=40, t=50, b=80)
    )
    return fig


def plot_feature_importance(features_dict: Dict[str, float]) -> go.Figure:
    """Plots horizontal bar chart of Random Forest feature importances."""
    if not features_dict:
        return go.Figure()

    df = pd.DataFrame([
        {"feature": k, "importance": v} for k, v in features_dict.items()
    ]).sort_values(by="importance", ascending=True)

    fig = go.Figure(go.Bar(
        x=df["importance"],
        y=df["feature"],
        orientation="h",
        marker=dict(color=CYAN)
    ))
    fig.update_layout(
        title="Feature importance (Random Forest)",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        xaxis_title="Relative Gini Importance",
        height=380,
        margin=dict(l=140, r=30, t=40, b=40),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR),
        yaxis=dict(showgrid=False)
    )
    return fig


def plot_station_fault_bars(station_data: List[Dict[str, Any]]) -> go.Figure:
    """Plots station-wise fault distribution breakdown."""
    if not station_data:
        return go.Figure()

    df = pd.DataFrame(station_data)
    fig = px.bar(
        df,
        x="station_id",
        y="count",
        color="severity",
        color_discrete_map={"CRITICAL": RED, "WARNING": AMBER, "NORMAL": GREEN},
        barmode="group",
        title="Fault incidents by station and severity"
    )
    fig.update_layout(
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, title="Incident Count")
    )
    return fig
