"""
Unit tests for Module 4: Machine Learning Predictor & Inference Engine.
"""
import pytest
from machine_learning.predict import GridPredictor


@pytest.fixture
def predictor():
    return GridPredictor()


def test_predictor_normal_reading(predictor):
    telemetry = {
        "sensor_id": "SNS-GS01-A-01",
        "station_id": "GS-01",
        "feeder_id": "FEEDER-A",
        "voltage_kv": 11.0,
        "current_a": 180.0,
        "frequency_hz": 50.0,
        "active_power_kw": 3400.0,
        "reactive_power_kvar": 1100.0,
        "power_factor": 0.95,
        "temperature_c": 45.0,
        "load_pct": 60.0,
        "breaker_status": "CLOSED"
    }
    result = predictor.predict_single(telemetry)
    assert "predicted_fault" in result
    assert "confidence" in result
    assert "severity" in result
    assert "anomaly_score" in result
    assert "localization_path" in result
    assert "recommended_action" in result
    assert 0.0 <= result["confidence"] <= 1.0


def test_predictor_short_circuit_fault(predictor):
    telemetry = {
        "sensor_id": "SNS-GS01-A-02",
        "station_id": "GS-01",
        "feeder_id": "FEEDER-A",
        "voltage_kv": 2.5,
        "current_a": 2500.0,
        "frequency_hz": 49.5,
        "active_power_kw": 4000.0,
        "reactive_power_kvar": 6000.0,
        "power_factor": 0.30,
        "temperature_c": 85.0,
        "load_pct": 300.0,
        "breaker_status": "TRIPPED"
    }
    result = predictor.predict_single(telemetry)
    assert result["predicted_fault"] == "Short Circuit"
    assert result["severity"] == "CRITICAL"
    assert result["is_anomaly"] is True
