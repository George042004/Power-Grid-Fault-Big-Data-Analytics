# ACADEMIC PROJECT REPORT

## POWER-GRID FAULT BIG-DATA ANALYTICS: A REAL-TIME BIG-DATA MONITORING PIPELINE BASED SOLUTION

**Submitted in Partial Fulfillment for the Degree of Bachelor of Technology in Computer Science & Engineering / Information Technology**

### Student Details
- **Student Name:** MARUMUDI GEORGE MULLAR
- **Project Guide:** Mr. R. SriRamu
- **Domain:** Big Data Analytics, Data Warehousing & Visualization
- **Academic Year:** 2025 – 2026

---

## TABLE OF CONTENTS
1. **Chapter 1: Introduction**
   - 1.1 Project Overview
   - 1.2 Motivation
   - 1.3 Problem Statement
   - 1.4 Project Objectives
2. **Chapter 2: Literature Survey & Existing Systems**
   - 2.1 Traditional SCADA and RTU Architectures
   - 2.2 Limitations of Existing Threshold-Based Relays
   - 2.3 Machine Learning in Smart Grids
3. **Chapter 3: Proposed System & System Architecture**
   - 3.1 Proposed Methodology
   - 3.2 Architectural Block Diagram
   - 3.3 Technology Stack
4. **Chapter 4: Modules Implementation & Data Engineering**
   - 4.1 Module 1: Synthetic Telemetry Generation
   - 4.2 Module 2: Real-Time Big-Data Streaming Architecture
   - 4.3 Module 3: Preprocessing & Domain Feature Engineering
   - 4.4 Module 4: Machine Learning Fault Diagnostics (RF & Isolation Forest)
   - 4.5 Module 5: Grid Fault Localization & Actionable Playbooks
   - 4.6 Module 6: Database Management & Warehousing (SQLite/SQLAlchemy)
   - 4.7 Module 7 & 8: Control-Room UI & Data Export (Streamlit)
   - 4.8 Module 9: High-Throughput REST API (FastAPI)
5. **Chapter 5: Experimental Results & Performance Analysis**
   - 5.1 Dataset Characteristics (7,000 Samples)
   - 5.2 Classification Metrics & Confusion Matrix
   - 5.3 Isolation Forest Anomaly Analysis
6. **Chapter 6: Conclusion & Future Scope**
   - 6.1 Summary of Contributions
   - 6.2 Future Enhancements
7. **References**

---

## CHAPTER 1: INTRODUCTION

### 1.1 Project Overview
Electrical power distribution grids are vast, distributed physical networks subject to dynamic load variations, environmental stresses, component aging, and transient short-circuits. Rapid detection, classification, and localization of electrical faults are critical to preventing catastrophic transformer explosions, wildfire ignition, and wide-area blackouts. This project implements an integrated real-time Big Data Analytics and Machine Learning monitoring pipeline to monitor 5 substations and multiple distribution feeders continuously.

### 1.2 Problem Statement
Conventional substation control systems rely on primitive fixed-threshold electromagnetic relays or isolated SCADA alarms. These legacy solutions:
1. Cannot easily detect complex multi-variable faults such as voltage sags, voltage swells, and progressive thermal degradation.
2. Produce overwhelming alarm storms without automated root-cause localization.
3. Lack integrated streaming data engineering pipelines to ingest, clean, and analyze high-frequency IoT sensor telemetry.

### 1.3 Project Objectives
- Engineer a high-fidelity synthetic AC power telemetry simulator covering 7 distinct operating conditions across 5 substations.
- Implement a decoupled streaming architecture supporting both Apache Kafka topics and high-speed in-memory local queues.
- Build automated data sanitization, missing-value imputation, deduplication, and domain feature engineering pipelines.
- Train supervised Random Forest and unsupervised Isolation Forest models for real-time diagnosis.
- Develop an industrial dark control-room dashboard and RESTful APIs providing real-time telemetry streaming, KPI metrics, and 1-click CSV data exports.

---

## CHAPTER 2: LITERATURE SURVEY & EXISTING SYSTEMS

| Author / System | Approach | Limitations | Proposed System Advancement |
| :--- | :--- | :--- | :--- |
| **Traditional SCADA** | Polling remote terminal units (RTUs) at 2–4s intervals with static thresholds | High latency, unable to diagnose transient power quality events | Sub-second streaming pipeline with continuous feature extraction |
| **Threshold Relays** | Fixed over-current and under-voltage triggers | Frequent false trips during motor starts and load surges | Random Forest classification incorporating multi-phase power triangle parameters |
| **Batch ML Pipelines** | Offline training on static historical CSV logs | No real-time streaming integration or live dashboard | Dual-mode streaming with continuous producer-consumer decoupling |

---

## CHAPTER 3: PROPOSED METHODOLOGY & ARCHITECTURE

The proposed architecture adopts a decoupled, multi-tiered pipeline:
1. **Telemetry Producer Tier:** Emits synchronized telemetry packets (voltage, current, frequency, active/reactive power, power factor, temperature, load percentage, breaker status).
2. **Streaming Buffer Tier:** Mirrors Kafka broker architecture (`powergrid.sensor.telemetry`, `powergrid.fault.monitoring`, `powergrid.processed.data`).
3. **Analytics Engine Tier:** Cleans, imputes, feature-engineers, and executes dual machine learning models.
4. **Data Warehouse Tier:** Persists time-stamped telemetry, predictions, and audit logs into indexed relational storage.
5. **Supervisory Interface Tier:** Exposes RESTful APIs via FastAPI and renders an interactive SCADA control-room via Streamlit.

---

## CHAPTER 4: IMPLEMENTATION DETAILS

### 4.1 AC Power Computations
Telemetry generator applies balanced 3-phase equations:
$$P = \sqrt{3} \cdot V_{\text{line}} \cdot I_{\text{line}} \cdot \cos(\theta)$$
$$Q = \sqrt{3} \cdot V_{\text{line}} \cdot I_{\text{line}} \cdot \sin(\theta)$$
$$S = \sqrt{P^2 + Q^2}$$
$$Z_{\text{est}} = \frac{V_{\text{line}} \times 1000}{I_{\text{line}} + \epsilon}$$

### 4.2 Machine Learning Formulations
- **Random Forest:** Ensemble of $B = 120$ bootstrap trees:
  $$\hat{C}(x) = \text{majority\_vote}\left(\{T_b(x)\}_{b=1}^B\right)$$
- **Isolation Forest:** Constructs recursive partitioning isolation trees where anomalies exhibit shorter average path length $h(x)$.

---

## CHAPTER 5: EXPERIMENTAL RESULTS

The pipeline was validated on a generated dataset of 7,000 records across 7 conditions.

- **Random Forest Classification Results:**
  - **Overall Accuracy:** $>98\%$
  - **Weighted Precision:** $>98\%$
  - **Weighted Recall:** $>98\%$
  - **Weighted F1-Score:** $>98\%$
- **Isolation Forest Anomaly Scoring:**
  - Accurately flagged short circuits, extreme overloads, and high thermal events with zero manual threshold tuning.

---

## CHAPTER 6: CONCLUSION & FUTURE SCOPE

The developed system demonstrates an end-to-end Big Data Analytics and Machine Learning engineering solution for smart electrical grids. The platform operates seamlessly on a standard Windows laptop using local streaming mode, while supporting enterprise Kafka clusters and Docker deployment.

**Future Enhancements:**
- Integration with phasor measurement units (PMUs) streaming IEEE C37.118 synchrophasors.
- Edge deployment onto NVIDIA Jetson or Raspberry Pi micro-substation nodes.
- Deep Learning time-series forecasting (LSTM / Transformers) for predictive fault anticipation.
