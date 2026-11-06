"""
Unit tests for Module 6: Database Management and CRUD operations.
"""
import pytest
from datetime import datetime
from database.db_manager import DatabaseManager


@pytest.fixture
def db():
    manager = DatabaseManager()
    manager.initialize_database()
    return manager


def test_database_initialization(db):
    stations = db.get_all_stations()
    assert len(stations) >= 5
    station_ids = [s["station_id"] for s in stations]
    assert "GS-01" in station_ids


def test_insert_and_get_sensor_reading(db):
    reading_payload = {
        "sensor_id": "SNS-TEST-01",
        "station_id": "GS-01",
        "feeder_id": "FEEDER-A",
        "voltage_kv": 11.05,
        "current_a": 182.4,
        "frequency_hz": 50.01,
        "active_power_kw": 3450.0,
        "reactive_power_kvar": 1100.0,
        "power_factor": 0.95,
        "temperature_c": 46.2,
        "load_pct": 61.0,
        "breaker_status": "CLOSED"
    }
    reading = db.insert_sensor_reading(reading_payload)
    assert reading is not None
    assert reading.id is not None

    recent = db.get_recent_readings(limit=10, station_id="GS-01")
    assert len(recent) > 0


def test_insert_fault_prediction(db):
    fault_payload = {
        "sensor_id": "SNS-TEST-02",
        "station_id": "GS-01",
        "feeder_id": "FEEDER-A",
        "predicted_fault": "Short Circuit",
        "confidence": 0.98,
        "severity": "CRITICAL",
        "localization_path": "GS-01 >> FEEDER-A >> SNS-TEST-02",
        "recommended_action": "Emergency isolation"
    }
    pred = db.insert_fault_prediction(fault_payload)
    assert pred is not None
    assert pred.id is not None

    faults = db.get_recent_faults(limit=5, severity="CRITICAL")
    assert len(faults) > 0


def test_analytics_summary_calculation(db):
    summary = db.get_analytics_summary()
    assert "total_readings" in summary
    assert "total_faults" in summary
    assert "active_stations" in summary
    assert summary["active_stations"] >= 5
    assert 0.0 <= summary["health_score"] <= 100.0
