"""
Unit tests for Module 3: Preprocessing & Feature Engineering.
"""
import pytest
import numpy as np
import pandas as pd
from preprocessing.clean_data import DataCleaner
from preprocessing.feature_engineering import FeatureEngineer


@pytest.fixture
def cleaner():
    return DataCleaner()


@pytest.fixture
def engineer():
    return FeatureEngineer()


def test_cleaner_single_reading_valid(cleaner):
    sample = {
        "voltage_kv": 11.2,
        "current_a": 185.0,
        "frequency_hz": 50.02,
        "active_power_kw": 3400.0,
        "reactive_power_kvar": 1100.0,
        "power_factor": 0.95,
        "temperature_c": 45.0,
        "load_pct": 62.0,
        "breaker_status": "CLOSED"
    }
    is_valid, sanitized, reason = cleaner.validate_reading_dict(sample)
    assert is_valid is True
    assert sanitized["voltage_kv"] == 11.2
    assert sanitized["breaker_status"] == "CLOSED"


def test_cleaner_imputes_missing(cleaner):
    sample = {
        "voltage_kv": None,
        "current_a": 180.0,
        "frequency_hz": np.nan,
        "active_power_kw": 3000.0,
        "reactive_power_kvar": 1000.0,
        "power_factor": 0.95,
        "temperature_c": 45.0,
        "load_pct": 60.0
    }
    is_valid, sanitized, _ = cleaner.validate_reading_dict(sample)
    assert sanitized["voltage_kv"] > 0
    assert sanitized["frequency_hz"] > 0


def test_cleaner_clips_outliers(cleaner):
    sample = {
        "voltage_kv": 150.0,  # extreme out of bounds
        "current_a": 180.0,
        "frequency_hz": 50.0,
        "active_power_kw": 3000.0,
        "reactive_power_kvar": 1000.0,
        "power_factor": 0.95,
        "temperature_c": 250.0,  # extreme temp
        "load_pct": 60.0
    }
    _, sanitized, _ = cleaner.validate_reading_dict(sample)
    assert sanitized["voltage_kv"] <= 60.0
    assert sanitized["temperature_c"] <= 160.0


def test_feature_engineering_computation(engineer):
    df = pd.DataFrame([{
        "voltage_kv": 11.0,
        "current_a": 200.0,
        "frequency_hz": 50.0,
        "active_power_kw": 3400.0,
        "reactive_power_kvar": 1100.0,
        "power_factor": 0.95,
        "temperature_c": 45.0,
        "load_pct": 65.0,
        "breaker_status": "CLOSED"
    }])
    feat_df = engineer.compute_features(df)
    assert "apparent_power_kva" in feat_df.columns
    assert "impedance_estimate_ohm" in feat_df.columns
    assert "voltage_deviation_pu" in feat_df.columns
    assert "frequency_deviation_hz" in feat_df.columns
    assert "breaker_is_tripped" in feat_df.columns
    assert feat_df["breaker_is_tripped"].iloc[0] == 0.0


def test_cleaner_keeps_33kv_station_voltage(cleaner):
    """GS-05 is a 33 kV hub: its normal readings must not be clipped to 25 kV."""
    sample = {"voltage_kv": 33.0, "current_a": 180.0, "frequency_hz": 50.0,
              "active_power_kw": 3000.0, "reactive_power_kvar": 1000.0,
              "power_factor": 0.95, "temperature_c": 45.0, "load_pct": 60.0}
    _, sanitized, _ = cleaner.validate_reading_dict(sample)
    assert sanitized["voltage_kv"] == 33.0


def test_voltage_deviation_uses_station_nominal():
    import pandas as pd
    from preprocessing.feature_engineering import FeatureEngineer
    df = pd.DataFrame([
        {"station_id": "GS-01", "voltage_kv": 11.0, "current_a": 180.0, "frequency_hz": 50.0,
         "active_power_kw": 3000.0, "reactive_power_kvar": 1000.0, "breaker_status": "CLOSED"},
        {"station_id": "GS-05", "voltage_kv": 33.0, "current_a": 180.0, "frequency_hz": 50.0,
         "active_power_kw": 3000.0, "reactive_power_kvar": 1000.0, "breaker_status": "CLOSED"},
    ])
    out = FeatureEngineer().compute_features(df)
    assert out["voltage_deviation_pu"].abs().max() < 1e-9
