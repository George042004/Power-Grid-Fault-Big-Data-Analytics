"""
Unit tests for Module 1: PowerGridSensorGenerator.
"""
import pytest
from scripts.generate_data import PowerGridSensorGenerator
from config.settings import settings


@pytest.fixture
def generator():
    return PowerGridSensorGenerator(random_seed=42)


def test_generator_initialization(generator):
    assert generator is not None
    assert len(generator.stations) == len(settings.GRID_STATIONS)


def test_generate_single_normal_reading(generator):
    reading = generator.generate_single_reading(condition="Normal")
    assert reading["target_condition"] == "Normal"
    assert "sensor_id" in reading
    assert "voltage_kv" in reading
    assert "current_a" in reading
    assert "frequency_hz" in reading
    assert "active_power_kw" in reading
    assert "reactive_power_kvar" in reading
    assert "power_factor" in reading
    assert "temperature_c" in reading
    assert "load_pct" in reading
    assert reading["breaker_status"] == "CLOSED"
    assert reading["is_valid"] is True


def test_generate_all_operating_conditions(generator):
    for condition in settings.FAULT_CLASSES:
        reading = generator.generate_single_reading(condition=condition)
        assert reading["target_condition"] == condition
        assert reading["voltage_kv"] > 0
        assert reading["current_a"] >= 0
        assert reading["frequency_hz"] > 0


def test_physics_relationships(generator):
    reading = generator.generate_single_reading(condition="Normal")
    v = reading["voltage_kv"]
    i = reading["current_a"]
    pf = reading["power_factor"]
    p = reading["active_power_kw"]
    # P approx sqrt(3) * V * I * pf
    expected_p = 1.73205 * v * i * pf
    assert abs(p - expected_p) / expected_p < 0.15  # within small noise margin


def test_generate_dataset_batch(generator):
    df = generator.generate_dataset(n_samples=70)
    assert len(df) == 70
    assert "target_condition" in df.columns
    assert set(df["target_condition"].unique()).issubset(set(settings.FAULT_CLASSES))
