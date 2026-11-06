"""
Unit tests for Module 5: Fault Localization & Maintenance Playbook.
"""
import pytest
from localization.fault_localizer import FaultLocalizer


@pytest.fixture
def localizer():
    return FaultLocalizer()


def test_localization_normal():
    loc = FaultLocalizer()
    res = loc.localize(
        predicted_fault="Normal",
        confidence=0.98,
        station_id="GS-01",
        feeder_id="FEEDER-A",
        sensor_id="SNS-GS01-A-01"
    )
    assert res["severity"] == "NORMAL"
    assert "GS-01" in res["localization_path"]
    assert "Routine" in res["recommended_action"]


def test_localization_short_circuit():
    loc = FaultLocalizer()
    res = loc.localize(
        predicted_fault="Short Circuit",
        confidence=0.99,
        station_id="GS-02",
        feeder_id="FEEDER-B",
        sensor_id="SNS-GS02-B-01"
    )
    assert res["severity"] == "CRITICAL"
    assert "GS-02" in res["localization_path"]
    assert "circuit breaker" in res["recommended_action"].lower()
    assert res["station_name"] == "South Industrial Hub"


def test_localization_overload():
    loc = FaultLocalizer()
    res = loc.localize(
        predicted_fault="Overload",
        confidence=0.92,
        station_id="GS-03",
        feeder_id="FEEDER-C",
        sensor_id="SNS-GS03-C-01"
    )
    assert res["severity"] == "WARNING"
    assert "load balancing" in res["recommended_action"].lower()
