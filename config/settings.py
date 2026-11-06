"""
System Settings and Environment Configuration.
Supports loading from environment variables or .env file with safe fallbacks.
"""
import os
from pathlib import Path
from typing import List

# Base Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env (if present) so values like API_PORT / STREAMING_MODE actually take effect.
# Real environment variables (e.g. from docker-compose) still take priority.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env", override=False)
except ImportError:
    pass
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
MODELS_DIR = BASE_DIR / "machine_learning" / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure runtime directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLE_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Settings:
    """Project-wide settings and configuration parameters."""
    
    # Base Project Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    RAW_DATA_DIR: Path = RAW_DATA_DIR
    PROCESSED_DATA_DIR: Path = PROCESSED_DATA_DIR
    SAMPLE_DATA_DIR: Path = SAMPLE_DATA_DIR
    MODELS_DIR: Path = MODELS_DIR
    REPORTS_DIR: Path = REPORTS_DIR

    # Project Identity
    PROJECT_TITLE: str = "Power-Grid Fault Big-Data Analytics"
    VERSION: str = "1.0.0"
    STUDENT_NAME: str = "MARUMUDI GEORGE MULLAR"
    PROJECT_GUIDE: str = "Mr. R. SriRamu"
    DOMAIN: str = "Big Data Analytics, Data Warehousing & Visualization"
    
    # Database Configuration
    DATABASE_FILE: Path = BASE_DIR / "power_grid.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_FILE}")
    
    # API Server Configuration
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Streamlit Dashboard Configuration
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "8501"))
    
    # Streaming Mode ("local" or "kafka")
    STREAMING_MODE: str = os.getenv("STREAMING_MODE", "local")
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_TELEMETRY: str = os.getenv("KAFKA_TOPIC_TELEMETRY", "powergrid.sensor.telemetry")
    KAFKA_TOPIC_FAULTS: str = os.getenv("KAFKA_TOPIC_FAULTS", "powergrid.fault.monitoring")
    KAFKA_TOPIC_PROCESSED: str = os.getenv("KAFKA_TOPIC_PROCESSED", "powergrid.processed.data")
    KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "powergrid_analytics_group")
    
    # Local Simulation Settings
    SIMULATION_INTERVAL_SEC: float = float(os.getenv("SIMULATION_INTERVAL_SEC", "1.0"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    FAULT_INJECTION_PROBABILITY: float = float(os.getenv("FAULT_INJECTION_PROBABILITY", "0.25"))
    
    # Grid Nominal Values
    NOMINAL_VOLTAGE_KV: float = 11.0  # 11 kV distribution grid
    NOMINAL_FREQUENCY_HZ: float = 50.0  # 50 Hz power grid frequency
    
    # Fault Classes Supported by Classifier
    FAULT_CLASSES: List[str] = [
        "Normal",
        "Overload",
        "Short Circuit",
        "Voltage Sag",
        "Voltage Swell",
        "Frequency Anomaly",
        "Overheating"
    ]
    
    # Standard Grid Stations Metadata
    GRID_STATIONS = [
        {"station_id": "GS-01", "name": "North Regional Substation", "region": "North Zone", "lat": 17.4485, "lon": 78.3908, "capacity_mva": 50.0, "nominal_kv": 11.0},
        {"station_id": "GS-02", "name": "South Industrial Hub", "region": "South Zone", "lat": 17.3616, "lon": 78.4747, "capacity_mva": 75.0, "nominal_kv": 11.0},
        {"station_id": "GS-03", "name": "East Tech Corridor Substation", "region": "East Zone", "lat": 17.4065, "lon": 78.5521, "capacity_mva": 60.0, "nominal_kv": 11.0},
        {"station_id": "GS-04", "name": "West Metro Traction Substation", "region": "West Zone", "lat": 17.4933, "lon": 78.3995, "capacity_mva": 40.0, "nominal_kv": 11.0},
        {"station_id": "GS-05", "name": "Central Grid Interchange Hub", "region": "Central Zone", "lat": 17.4123, "lon": 78.4483, "capacity_mva": 100.0, "nominal_kv": 33.0},
    ]


settings = Settings()
