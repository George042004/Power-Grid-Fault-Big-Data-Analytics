# Project Documentation: Power-Grid Fault Big-Data Analytics

### Real-Time Big-Data Monitoring Pipeline Based Solution

**Candidate:** MARUMUDI GEORGE MULLAR  
**Project Guide:** Mr. R. SriRamu  
**Academic Domain:** Big Data Analytics, Data Warehousing & Visualization  

---

## 1. Abstract
Modern electrical power transmission and distribution networks require high-frequency automated monitoring to prevent cascading blackouts, reduce equipment damage, and safeguard grid stability. This project develops an end-to-end Big Data Analytics and Machine Learning pipeline that simulates, streams, sanitizes, classifies, and localizes power-grid faults in real time. The solution integrates an AC electrical telemetry simulator, a multi-threaded streaming architecture (supporting both Apache Kafka and local in-memory queues), a data sanitization and feature engineering pipeline, Random Forest multi-class classification, Isolation Forest anomaly scoring, and an industrial-grade Streamlit control-room dashboard with FastAPI REST backends.

---

## 2. Operating Conditions & Fault Taxonomy

The system monitors and diagnoses 7 distinct power-grid operational conditions:

| Condition | Electrical Signature | Primary Sensor Indicators | Operational Severity |
| :--- | :--- | :--- | :---: |
| **Normal** | Balanced steady-state AC operations | $V \approx 11.0\text{ kV}$, $I \approx 110-250\text{ A}$, $f \approx 50.0\text{ Hz}$, $T \approx 45^\circ\text{C}$ | `NORMAL` |
| **Overload** | Continuous current beyond thermal rating | $I \approx 380-600\text{ A}$, Load $>120\%$, $T \approx 70-92^\circ\text{C}$, slight voltage drop | `WARNING` |
| **Short Circuit** | Low-impedance fault; immediate arc current | $I \approx 1200-2800\text{ A}$, $V \text{ plunges to } 1.5-4.8\text{ kV}$, Breaker Trips | `CRITICAL` |
| **Voltage Sag** | Transient under-voltage from motor start/line trip | $V \text{ drops to } 0.55-0.84\text{ pu}$ ($6.0-9.2\text{ kV}$), normal/distorted current | `WARNING` |
| **Voltage Swell** | Transient over-voltage from load shedding | $V \text{ surges to } 1.15-1.45\text{ pu}$ ($12.5-16.0\text{ kV}$), reactive surge | `WARNING` |
| **Frequency Anomaly** | Active power generation-load imbalance | $f < 49.1\text{ Hz}$ or $f > 51.0\text{ Hz}$ outside statutory grid code | `WARNING` |
| **Overheating** | Transformer cooling failure or contact resistance | $T \approx 92-135^\circ\text{C}$ while electrical parameters are near rated | `CRITICAL` |

---

## 3. Data Engineering & Preprocessing Workflow

1. **Sliding-Window Deduplication:** Computes hash fingerprints ($SensorID \parallel Timestamp \parallel Voltage \parallel Current$) over a 5,000-message sliding deque to discard duplicate network packets.
2. **Missing-Value Imputation:** Imputes missing or null telemetry channels using median fallback parameters.
3. **Physical Bound Verification:** Clamps noise artifacts into physically feasible operational bounds (e.g. voltage bounded between $0.5\text{ kV}$ and $25\text{ kV}$).
4. **Domain Feature Engineering:** Computes Apparent Power ($S = \sqrt{P^2 + Q^2}$), Apparent Impedance ($Z \approx V/I$), Per-Unit Voltage Deviation ($\Delta V = |V - V_{\text{nom}}| / V_{\text{nom}}$), and Frequency Deviation ($\Delta f = |f - 50.0|$).
5. **Standard Scaling:** Normalizes continuous electrical features with zero mean and unit variance.

---

## 4. Machine Learning Models

### Random Forest Classifier
- **Algorithm:** Ensemble of 120 randomized decision trees with balanced class weighting.
- **Input Features:** Voltage, Current, Frequency, Active Power, Reactive Power, Power Factor, Temperature, Load Percentage, Apparent Power, Impedance Estimate, Per-Unit Voltage Deviation, Frequency Deviation, Breaker Tripped flag.
- **Target Classes:** 7 mutually exclusive operational conditions.
- **Performance:** Achieves $>98\%$ accuracy, precision, recall, and F1-score across stratified test partitions.

### Isolation Forest Anomaly Detection
- **Algorithm:** Unsupervised ensemble isolating anomalies via recursive random partitioning.
- **Role:** Flags novel or unanticipated grid abnormalities independent of supervised label taxonomy.
- **Metric:** Computes decision score and flags readings below contamination threshold ($12\%$).

---

## 5. Topological Fault Localization & Maintenance Directives
When a fault is classified, the system maps the node across the electrical distribution hierarchy:
$$\text{Station ID } (\text{e.g. GS-01 North Regional Substation}) \longrightarrow \text{Feeder ID } (\text{FEEDER-A}) \longrightarrow \text{Sensor Node } (\text{SNS-GS01-A-01})$$

The engine dynamically pairs each incident with an actionable maintenance procedure, advising field operators on breaker lockout verification, load balancing, tap-changer regulation, or infrared thermography scans.
