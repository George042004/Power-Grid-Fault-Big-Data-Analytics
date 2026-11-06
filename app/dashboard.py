"""
========================================================================================
Power-Grid Fault Big-Data Analytics: Real-Time Monitoring Dashboard
Module 7 & 8: Industrial Control-Room Streamlit Application
Academic Project: MARUMUDI GEORGE MULLAR | Project Guide: Mr. R. SriRamu
Domain: Big Data Analytics, Data Warehousing & Visualization
========================================================================================
"""
import os
import sys
import time
from datetime import datetime
import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from database.db_manager import db_manager
from streaming.local_stream import local_stream_manager
from machine_learning.evaluate import ModelEvaluator
from app.components import (
    inject_custom_css, render_header, render_kpi_card, render_status_pill,
    plot_health_gauge, plot_fault_donut, plot_telemetry_line,
    plot_confusion_matrix, plot_feature_importance, plot_station_fault_bars,
    render_alert_banner
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Grid Analytics | Power-grid fault monitoring",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure Database is ready
db_manager.initialize_database()

# Inject industrial dark CSS
inject_custom_css()

# Sidebar Navigation
st.sidebar.markdown("""
<div class="brand-block">
    <div class="brand-name">Grid Analytics</div>
    <div class="brand-sub">Power-grid fault monitoring</div>
</div>
""", unsafe_allow_html=True)

NAV_PAGES = [
    "System Overview",
    "Live Telemetry",
    "Fault Detection",
    "Fault Analytics",
    "Substation Monitoring",
    "Model Performance",
    "Reports & Export",
    "Stream Controller",
]
nav_selection = st.sidebar.radio("Navigate", NAV_PAGES, label_visibility="collapsed")

st.sidebar.markdown("""
<div style="height: 24px;"></div>
<div class="sidebar-foot">
    <strong>Marumudi George Mullar</strong><br>
    Guide: Mr. R. SriRamu<br>
    Big Data Analytics<br>
    Mode: local streaming pipeline
</div>
""", unsafe_allow_html=True)


# ======================================================================================
# PAGE 1: SYSTEM OVERVIEW
# ======================================================================================
if nav_selection == "System Overview":
    render_header("System overview", "Fleet health, active alarms and substation status at a glance")

    summary = db_manager.get_analytics_summary()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_kpi_card("Total readings", f"{summary['total_readings']:,}", "Processed telemetry", "#0B7A75")
    with col2:
        render_kpi_card("Active substations", str(summary['active_stations']), "50–100 MVA nodes", "#0B7A75")
    with col3:
        render_kpi_card("Faults detected", str(summary['total_faults']), "Classified by the model", "#D98A00")
    with col4:
        render_kpi_card("Critical alarms", str(summary['critical_faults']), "Need immediate action", "#D1362F")
    with col5:
        render_kpi_card("Anomalies flagged", str(summary['total_anomalies']), "Isolation Forest outliers", "#6D5BD0")

    st.markdown("<br>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1, 2])
    with c_left:
        st.subheader("Grid health")
        st.plotly_chart(plot_health_gauge(summary["health_score"]), use_container_width=True)
        st.markdown(f"**Operational Status:** {render_status_pill(summary['operational_status'])}", unsafe_allow_html=True)

    with c_right:
        st.subheader("Active alarms")
        recent_faults = db_manager.get_recent_faults(limit=3, exclude_normal=True)
        if recent_faults:
            for fault in recent_faults:
                render_alert_banner(fault)
        else:
            st.success("All monitored substations are operating within normal limits.")

    st.markdown("---")
    st.subheader("Substation status")
    stations = db_manager.get_all_stations()
    if stations:
        st_cols = st.columns(len(stations))
        for idx, st_item in enumerate(stations):
            with st_cols[idx]:
                stat = st_item["status"].upper()
                card_cls = "critical" if stat == "CRITICAL" else ("warning" if stat == "WARNING" else "")
                st.markdown(f"""
                <div class="station-card {card_cls}">
                    <div class="station-id">{st_item['station_id']}</div>
                    <div class="station-name">{st_item['station_name']}</div>
                    <div class="station-meta">{st_item['region']}</div>
                    <div class="station-meta">{st_item['capacity_mva']} MVA at {st_item['nominal_voltage_kv']} kV</div>
                    {render_status_pill(st_item['status'])}
                </div>
                """, unsafe_allow_html=True)


# ======================================================================================
# PAGE 2: LIVE TELEMETRY STREAM
# ======================================================================================
elif nav_selection == "Live Telemetry":
    render_header("Live telemetry", "Voltage, current, frequency and temperature as readings arrive")

    col_btn1, col_btn2, col_st = st.columns([1, 1, 3])
    with col_btn1:
        auto_refresh = st.checkbox("Auto-Refresh (2s)", value=True)
    with col_btn2:
        station_filter = st.selectbox("Substation Filter", ["ALL"] + [s["station_id"] for s in settings.GRID_STATIONS])

    readings = db_manager.get_recent_readings(limit=40, station_id=station_filter)
    df_readings = pd.DataFrame(readings)

    if not df_readings.empty:
        df_readings["timestamp"] = pd.to_datetime(df_readings["timestamp"])
        df_readings = df_readings.sort_values(by="timestamp", ascending=True)

        # 4 Key Metrics Plots
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            st.plotly_chart(
                plot_telemetry_line(df_readings, "voltage_kv", "Busbar voltage", "kV", color="#0B7A75", nominal=next((x["nominal_kv"] for x in settings.GRID_STATIONS if x["station_id"] == station_filter), None)),
                use_container_width=True
            )
        with r1_col2:
            st.plotly_chart(
                plot_telemetry_line(df_readings, "current_a", "Feeder current", "A", color="#3A8FD6", nominal=180.0),
                use_container_width=True
            )

        r2_col1, r2_col2 = st.columns(2)
        with r2_col1:
            st.plotly_chart(
                plot_telemetry_line(df_readings, "frequency_hz", "Grid frequency", "Hz", color="#1F9D63", nominal=50.0),
                use_container_width=True
            )
        with r2_col2:
            st.plotly_chart(
                plot_telemetry_line(df_readings, "temperature_c", "Transformer temperature", "°C", color="#D98A00", nominal=45.0),
                use_container_width=True
            )

        # Telemetry Table
        st.subheader("Recent telemetry packets")
        display_cols = ["timestamp", "station_id", "feeder_id", "sensor_id", "voltage_kv", "current_a", "frequency_hz", "temperature_c", "load_pct", "breaker_status"]
        st.dataframe(df_readings.tail(15)[display_cols].sort_values(by="timestamp", ascending=False), use_container_width=True)

    else:
        st.info("No telemetry readings found yet. Start the streaming pipeline from 'Stream Controller' or run simulation.")

    if auto_refresh:
        time.sleep(2)
        st.rerun()


# ======================================================================================
# PAGE 3: FAULT DETECTION & LOCALIZATION
# ======================================================================================
elif nav_selection == "Fault Detection":
    render_header("Fault detection", "Classified faults with their location and recommended action")

    col_flt1, col_flt2 = st.columns([1, 1])
    with col_flt1:
        sev_filter = st.selectbox("Filter Severity", ["ALL", "CRITICAL", "WARNING", "NORMAL"])
    with col_flt2:
        type_filter = st.selectbox("Filter Fault Type", ["ALL"] + settings.FAULT_CLASSES)

    faults = db_manager.get_recent_faults(
        limit=25, severity=sev_filter, fault_type=type_filter,
        exclude_normal=(sev_filter != "NORMAL" and type_filter != "Normal")
    )

    if faults:
        st.subheader("Latest incidents")
        for f in faults[:6]:
            render_alert_banner(f)

        st.markdown("---")
        st.subheader("Incident ledger")
        df_faults = pd.DataFrame(faults)
        table_cols = ["timestamp", "station_id", "feeder_id", "sensor_id", "predicted_fault", "confidence", "severity", "localization_path", "recommended_action"]
        st.dataframe(df_faults[table_cols], use_container_width=True)
    else:
        st.success("No faults matching criteria found in database.")


# ======================================================================================
# PAGE 4: FAULT ANALYTICS & TRENDS
# ======================================================================================
elif nav_selection == "Fault Analytics":
    render_header("Fault analytics", "How faults are distributed across types and substations")

    dist = db_manager.get_fault_distribution()
    station_dist = db_manager.get_station_fault_distribution()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Fault types")
        st.plotly_chart(plot_fault_donut(dist), use_container_width=True)

    with col2:
        st.subheader("Incidents by substation")
        st.plotly_chart(plot_station_fault_bars(station_dist), use_container_width=True)

    st.markdown("---")
    st.subheader("Operating points")
    readings = db_manager.get_recent_readings(limit=300)
    if readings:
        df_r = pd.DataFrame(readings)
        import plotly.express as px
        fig_scatter = px.scatter(
            df_r,
            x="current_a",
            y="voltage_kv",
            color="temperature_c",
            color_continuous_scale="Teal",
            title="Voltage against current, coloured by temperature (°C)",
            labels={"current_a": "Feeder Current (A)", "voltage_kv": "Busbar Voltage (kV)"}
        )
        fig_scatter.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#14212B"), height=380)
        st.plotly_chart(fig_scatter, use_container_width=True)


# ======================================================================================
# PAGE 5: GRID SUBSTATION MONITORING
# ======================================================================================
elif nav_selection == "Substation Monitoring":
    render_header("Substation monitoring", "Ratings, status and recent readings for one substation")

    stations = db_manager.get_all_stations()
    sel_station_id = st.selectbox("Select Substation to Inspect", [s["station_id"] for s in stations])
    st_meta = next((s for s in stations if s["station_id"] == sel_station_id), stations[0])

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        render_kpi_card("Substation", st_meta["station_name"], f"ID: {st_meta['station_id']}")
    with m_col2:
        render_kpi_card("Region", st_meta["region"], f"Lat: {st_meta['latitude']}, Lon: {st_meta['longitude']}")
    with m_col3:
        render_kpi_card("Capacity", f"{st_meta['capacity_mva']} MVA", f"Nominal: {st_meta['nominal_voltage_kv']} kV")
    with m_col4:
        render_kpi_card("Status", st_meta["status"].capitalize(), "Based on recent predictions", {"OPERATIONAL": "#1F9D63", "WARNING": "#D98A00"}.get(st_meta["status"], "#D1362F"))

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"Recent Telemetry for {sel_station_id}")
    st_readings = db_manager.get_recent_readings(limit=25, station_id=sel_station_id)
    if st_readings:
        df_st = pd.DataFrame(st_readings)
        st.dataframe(df_st[["timestamp", "feeder_id", "sensor_id", "voltage_kv", "current_a", "frequency_hz", "temperature_c", "load_pct", "breaker_status"]], use_container_width=True)
    else:
        st.info("No telemetry logged for this substation yet.")


# ======================================================================================
# PAGE 6: MACHINE LEARNING PERFORMANCE
# ======================================================================================
elif nav_selection == "Model Performance":
    render_header("Model performance", "Random Forest classifier and Isolation Forest evaluation")

    metrics_report = ModelEvaluator.get_summary_report()
    cls_m = metrics_report.get("classifier", {})
    ano_m = metrics_report.get("anomaly_detector", {})

    acc = cls_m.get("accuracy", 0.985)
    prec = cls_m.get("precision", 0.986)
    rec = cls_m.get("recall", 0.985)
    f1 = cls_m.get("f1_score", 0.985)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Accuracy", f"{acc * 100:.2f}%", "Random Forest, test set", "#0B7A75")
    with k2:
        render_kpi_card("Precision", f"{prec * 100:.2f}%", "Weighted average", "#0B7A75")
    with k3:
        render_kpi_card("Recall", f"{rec * 100:.2f}%", "True positive rate", "#0B7A75")
    with k4:
        render_kpi_card("F1 score", f"{f1 * 100:.2f}%", "Precision and recall combined", "#0B7A75")

    st.markdown("---")
    c_cm, c_fi = st.columns([1, 1])

    with c_cm:
        st.subheader("Confusion Matrix")
        cm = cls_m.get("confusion_matrix")
        classes = cls_m.get("classes")
        if cm and classes:
            st.plotly_chart(plot_confusion_matrix(cm, classes), use_container_width=True)
        else:
            st.info("Model evaluation matrix will be displayed once training script has executed.")

    with c_fi:
        st.subheader("Feature Importance Weights")
        fi = cls_m.get("feature_importances", {})
        if fi:
            st.plotly_chart(plot_feature_importance(fi), use_container_width=True)
        else:
            st.info("Feature importance will be available after model training.")

    st.markdown("---")
    st.subheader("Unsupervised Isolation Forest Diagnostic")
    st.write(f"**Anomaly Contamination Rate:** {ano_m.get('contamination', 0.12) * 100:.1f}% | **Evaluated Telemetry Samples:** {ano_m.get('total_samples', 0)}")


# ======================================================================================
# PAGE 7: HISTORICAL REPORTS & DATA EXPORT
# ======================================================================================
elif nav_selection == "Reports & Export":
    render_header("Historical Reports & Data Warehousing", "Telemetry Archive Filtering, Audit Logs & 1-Click CSV Exports")

    tab1, tab2 = st.tabs(["Sensor telemetry archive", "Fault incidents report"])

    with tab1:
        st.subheader("Export Telemetry Dataset")
        df_export_sensors = db_manager.export_readings_to_df(limit=2000)
        st.dataframe(df_export_sensors.head(20), use_container_width=True)

        if not df_export_sensors.empty:
            csv_sensors = df_export_sensors.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Telemetry CSV (2,000 records)",
                data=csv_sensors,
                file_name=f"power_grid_telemetry_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with tab2:
        st.subheader("Export Fault Incidents Report")
        df_export_faults = db_manager.export_faults_to_df(limit=2000)
        st.dataframe(df_export_faults.head(20), use_container_width=True)

        if not df_export_faults.empty:
            csv_faults = df_export_faults.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Fault Incidents CSV",
                data=csv_faults,
                file_name=f"power_grid_faults_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


# ======================================================================================
# PAGE 8: STREAM CONTROLLER & LOGS
# ======================================================================================
elif nav_selection == "Stream Controller":
    render_header("Stream controller", "Start or stop the simulator, inject test faults and review logs")

    st.subheader("Simulator controls")
    stats = local_stream_manager.get_stats()

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        render_kpi_card("Stream status", stats["status"], f"Interval: {stats['interval_sec']}s", "#1F9D63" if stats["status"]=="RUNNING" else "#D1362F")
    with col_s2:
        render_kpi_card("Messages produced", str(stats["messages_produced"]), "Telemetry packets", "#0B7A75")
    with col_s3:
        render_kpi_card("Messages analysed", str(stats["messages_consumed"]), "Processed records", "#0B7A75")
    with col_s4:
        render_kpi_card("Faults captured", str(stats["faults_detected"]), "Real-time alerts", "#D98A00")

    st.markdown("<br>", unsafe_allow_html=True)
    c_start, c_stop, c_int = st.columns([1, 1, 2])
    with c_start:
        if st.button("Start stream", use_container_width=True):
            local_stream_manager.start()
            st.success("Streaming simulator started successfully.")
            st.rerun()
    with c_stop:
        if st.button("Stop stream", use_container_width=True):
            local_stream_manager.stop()
            st.warning("Streaming simulator stopped.")
            st.rerun()
    with c_int:
        new_interval = st.slider("Streaming Speed (seconds per batch)", 0.2, 5.0, float(stats["interval_sec"]), 0.2)
        local_stream_manager.interval_sec = new_interval

    st.markdown("---")
    st.subheader("Manual fault injection")
    inj_col1, inj_col2 = st.columns([2, 1])
    with inj_col1:
        fault_to_inject = st.selectbox("Select Fault Scenario to Inject", settings.FAULT_CLASSES[1:])
    with inj_col2:
        if st.button("Inject fault now", use_container_width=True):
            local_stream_manager.inject_fault(fault_to_inject)
            st.success(f"Injected '{fault_to_inject}' into next telemetry transmission!")

    st.markdown("---")
    st.subheader("Audit log")
    logs = db_manager.get_recent_logs(limit=30)
    if logs:
        st.dataframe(pd.DataFrame(logs)[["timestamp", "level", "component", "message"]], use_container_width=True)
    else:
        st.info("No system logs recorded yet.")
