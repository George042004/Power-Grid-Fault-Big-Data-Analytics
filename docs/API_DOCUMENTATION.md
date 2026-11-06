# Power-Grid Fault Big-Data Analytics: REST API Reference

**Interactive OpenAPI Documentation:** Available at `http://127.0.0.1:8000/docs` (Swagger UI) and `http://127.0.0.1:8000/redoc`.

---

## 1. System Health

### `GET /health`
Returns system status, active database connection, and streaming mode.

**Response:**
```json
{
  "status": "HEALTHY",
  "timestamp": "2026-11-04T10:00:00.000000",
  "project": "Power-Grid Fault Big-Data Analytics",
  "version": "1.0.0",
  "database": "CONNECTED",
  "streaming_mode": "local"
}
```

---

## 2. Sensors & Telemetry

### `GET /sensors`
Returns paginated sensor telemetry readings.

**Query Parameters:**
- `limit` (int, default=50, max=500): Number of readings to return.
- `station_id` (str, optional): Filter by substation (e.g. `GS-01`).

### `GET /sensors/latest`
Returns latest telemetry readings across all substations.

---

## 3. Grid Substations

### `GET /stations`
Returns list of all monitored grid substations with geographical and electrical metadata.

**Response Schema:**
```json
[
  {
    "station_id": "GS-01",
    "station_name": "North Regional Substation",
    "region": "North Zone",
    "latitude": 17.4485,
    "longitude": 78.3908,
    "nominal_voltage_kv": 11.0,
    "capacity_mva": 50.0,
    "status": "OPERATIONAL"
  }
]
```

---

## 4. Fault Detection & Diagnostics

### `GET /faults`
Returns classified fault records with localization paths and maintenance recommendations.

**Query Parameters:**
- `limit` (int, default=50): Records to return.
- `station_id` (str, optional): Filter by station.
- `severity` (str, optional): Filter by `CRITICAL`, `WARNING`, or `NORMAL`.
- `fault_type` (str, optional): Filter by fault class (e.g., `Short Circuit`, `Overload`).

### `GET /faults/latest`
Returns recent fault incidents ordered by timestamp descending.

---

## 5. Analytics & Model Performance

### `GET /analytics/summary`
Returns aggregate KPI metrics:
```json
{
  "total_readings": 7000,
  "total_faults": 1250,
  "normal_readings": 5750,
  "total_anomalies": 840,
  "active_stations": 5,
  "critical_faults": 320,
  "warning_faults": 930,
  "health_score": 96.4,
  "operational_status": "NORMAL"
}
```

### `GET /analytics/fault-distribution`
Returns frequency counts grouped by fault category.

### `GET /model/metrics`
Returns machine learning evaluation metrics, confusion matrix, and feature importances.

---

## 6. Simulation & Stream Controls

### `POST /simulation/start`
Starts the real-time background telemetry streaming pipeline.
```json
{
  "interval_sec": 1.0,
  "fault_probability": 0.25
}
```

### `POST /simulation/stop`
Halts the real-time background telemetry streaming pipeline.

### `GET /simulation/status`
Returns throughput metrics (messages produced, messages consumed, queue sizes).

### `POST /simulation/inject-fault`
Schedules an immediate on-demand fault scenario injection for testing.
```json
{
  "fault_type": "Short Circuit"
}
```

---

## 7. System Operations Logs

### `GET /logs`
Returns recent operations, streaming events, and audit logs.
