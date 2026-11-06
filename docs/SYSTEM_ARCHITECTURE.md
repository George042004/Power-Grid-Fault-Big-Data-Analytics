# System Architecture: Power-Grid Fault Big-Data Analytics

## Real-Time Monitoring Pipeline Based Solution

**Author:** MARUMUDI GEORGE MULLAR  
**Project Guide:** Mr. R. SriRamu  
**Domain:** Big Data Analytics, Data Warehousing & Visualization  

---

## 1. High-Level Architectural Flowchart

```mermaid
flowchart TD
    subgraph Data_Generation [Module 1: Synthetic Telemetry Generation]
        G1[Station GS-01: North]
        G2[Station GS-02: South]
        G3[Station GS-03: East]
        G4[Station GS-04: West]
        G5[Station GS-05: Central Hub]
        GEN[PowerGridSensorGenerator] --> G1 & G2 & G3 & G4 & G5
    end

    subgraph Streaming_Layer [Module 2: Real-Time Big-Data Streaming]
        GEN -->|Raw Telemetry Packets| PROD[Kafka Producer / Local In-Memory Queue]
        PROD --> T1[(Topic: sensor.telemetry)]
        PROD --> T2[(Topic: fault.monitoring)]
        PROD --> T3[(Topic: processed.data)]
        T1 --> CONS[Data Consumer Engine]
    end

    subgraph Processing_Layer [Module 3: Preprocessing & Feature Engineering]
        CONS --> DEDUP[Sliding-Window Deduplication]
        DEDUP --> CLEAN[Data Sanitization & Bounds Clamping]
        CLEAN --> FEAT[Domain Electrical Feature Engineering: S, Z, dV, df]
    end

    subgraph Intelligence_Layer [Module 4 & 5: Machine Learning & Localization]
        FEAT --> RF[Random Forest Multi-Class Fault Classifier]
        FEAT --> IF[Isolation Forest Unsupervised Anomaly Detector]
        RF --> LOC[Topological Fault Localizer: Station >> Feeder >> Sensor]
        IF --> LOC
    end

    subgraph Storage_Layer [Module 6: Database & Warehousing]
        LOC --> DB[(SQLite Database: power_grid.db)]
        DB --> TBL1[grid_stations]
        DB --> TBL2[sensor_readings]
        DB --> TBL3[fault_predictions]
        DB --> TBL4[anomaly_records]
        DB --> TBL5[system_logs]
    end

    subgraph Presentation_Layer [Module 7, 8, 9: FastAPI & Streamlit]
        DB --> API[FastAPI Backend REST Service: Port 8000]
        API --> SWAG[Swagger UI Documentation /docs]
        DB --> DASH[Streamlit Control-Room Dashboard: Port 8501]
        DASH --> V1[Live Telemetry Charts]
        DASH --> V2[Diagnostic KPI Gauges]
        DASH --> V3[Fault Playbook Directives]
        DASH --> V4[1-Click CSV Exports]
    end
```

---

## 2. Component Design Specifications

### A. Telemetry Generation Layer
- Simulates realistic 3-phase AC distribution voltage ($11\text{ kV}$ nominal) and frequency ($50.0\text{ Hz}$ synchronous).
- Injects 7 operational states: Normal, Overload, Short Circuit, Voltage Sag, Voltage Swell, Frequency Anomaly, and Overheating.
- Calculates active power ($P$), reactive power ($Q$), and apparent power ($S$) through physical AC power triangle formulations.

### B. Streaming Architecture
- **Dual-Mode Streaming Support:**
  - **Local Mode (Default):** Multi-threaded in-memory queues mirroring Kafka topics with sliding-window fingerprint deduplication. Allows instant zero-configuration execution on Windows laptops.
  - **Kafka Mode:** Connects to Apache Kafka clusters publishing to `powergrid.sensor.telemetry` and consumer groups.

### C. Machine Learning Diagnostic Engine
- **Random Forest Classifier:**
  - 120 decision trees, max depth of 15, balanced class weighting.
  - Evaluated on test set with 98%+ Accuracy, Precision, Recall, and F1-Score.
- **Isolation Forest:**
  - Unsupervised outlier scoring identifying anomalous grid behavior.
- **Topological Fault Localizer:**
  - Maps anomalies to `Station >> Feeder >> Sensor` hierarchical paths and outputs maintenance action playbooks.

### D. Data Persistence & Presentation
- **SQLite + SQLAlchemy ORM:** Thread-safe ACID persistence with indexed timestamp searches.
- **FastAPI:** Non-blocking async endpoints exposing REST interfaces and simulation controls.
- **Streamlit:** Industrial dark navy control-room user interface with interactive Plotly telemetry graphs.
