-- ====================================================================
-- Power-Grid Fault Big-Data Analytics Database Schema (SQLite compatible)
-- Academic Project: MARUMUDI GEORGE MULLAR | Guide: Mr. R. SriRamu
-- ====================================================================

-- 1. Grid Substations Table
CREATE TABLE IF NOT EXISTS grid_stations (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(150) NOT NULL,
    region VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    nominal_voltage_kv FLOAT DEFAULT 11.0,
    capacity_mva FLOAT DEFAULT 50.0,
    status VARCHAR(50) DEFAULT 'OPERATIONAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Power-Grid Sensor Readings (Telemetry) Table
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    station_id VARCHAR(50) NOT NULL,
    feeder_id VARCHAR(50) NOT NULL,
    voltage_kv FLOAT NOT NULL,
    current_a FLOAT NOT NULL,
    frequency_hz FLOAT NOT NULL,
    active_power_kw FLOAT NOT NULL,
    reactive_power_kvar FLOAT NOT NULL,
    power_factor FLOAT NOT NULL,
    temperature_c FLOAT NOT NULL,
    load_pct FLOAT NOT NULL,
    breaker_status VARCHAR(20) DEFAULT 'CLOSED',
    is_valid BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES grid_stations (station_id)
);

CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_readings (timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_station_feeder ON sensor_readings (station_id, feeder_id);

-- 3. Fault Predictions (Machine Learning Classification) Table
CREATE TABLE IF NOT EXISTS fault_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reading_id INTEGER,
    sensor_id VARCHAR(50) NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    feeder_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_fault VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    localization_path VARCHAR(200) NOT NULL,
    recommended_action TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES sensor_readings (id),
    FOREIGN KEY (station_id) REFERENCES grid_stations (station_id)
);

CREATE INDEX IF NOT EXISTS idx_fault_type ON fault_predictions (predicted_fault);
CREATE INDEX IF NOT EXISTS idx_fault_severity ON fault_predictions (severity);
CREATE INDEX IF NOT EXISTS idx_fault_station ON fault_predictions (station_id);

-- 4. Anomaly Records (Unsupervised Isolation Forest) Table
CREATE TABLE IF NOT EXISTS anomaly_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reading_id INTEGER,
    sensor_id VARCHAR(50) NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    anomaly_score FLOAT NOT NULL,
    is_anomaly BOOLEAN NOT NULL DEFAULT 0,
    metric_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES sensor_readings (id),
    FOREIGN KEY (station_id) REFERENCES grid_stations (station_id)
);

CREATE INDEX IF NOT EXISTS idx_anomaly_status ON anomaly_records (is_anomaly);

-- 5. System Logs Table
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL DEFAULT 'INFO',
    component VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_log_level ON system_logs (level);
