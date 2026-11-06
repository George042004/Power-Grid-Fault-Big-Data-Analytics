"""
Feature Engineering Pipeline.
Derives domain-specific electrical features, impedance ratios, and scales features for ML.
"""
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings


class FeatureEngineer:
    """
    Computes derived electrical grid features and formats input vectors for ML inference.
    """

    # Primary numerical features to train and predict
    BASE_NUMERICAL_COLS = [
        "voltage_kv",
        "current_a",
        "frequency_hz",
        "active_power_kw",
        "reactive_power_kvar",
        "power_factor",
        "temperature_c",
        "load_pct",
    ]

    # Engineered domain features
    DERIVED_FEATURE_COLS = [
        "apparent_power_kva",
        "impedance_estimate_ohm",
        "voltage_deviation_pu",
        "frequency_deviation_hz",
        "breaker_is_tripped"
    ]

    ALL_FEATURE_COLS = BASE_NUMERICAL_COLS + DERIVED_FEATURE_COLS

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates domain-engineered electrical power system metrics:
        - Apparent power S = sqrt(P^2 + Q^2)
        - Estimated apparent impedance Z = (V * 1000) / (I + eps)
        - Per-unit voltage deviation = |V - V_nom| / V_nom
        - Absolute frequency deviation = |f - f_nom|
        - Binary circuit breaker trip flag
        """
        feat_df = df.copy()

        # 1. Apparent Power (kVA)
        p = feat_df["active_power_kw"]
        q = feat_df["reactive_power_kvar"]
        feat_df["apparent_power_kva"] = np.sqrt(p ** 2 + q ** 2)

        # 2. Impedance Estimate (Ohms) Z = (V * 1000) / (I + 0.01)
        v_volts = feat_df["voltage_kv"] * 1000.0
        i_amps = feat_df["current_a"] + 0.01
        feat_df["impedance_estimate_ohm"] = v_volts / i_amps
        # Clip extreme impedances (e.g. open circuit or noise)
        feat_df["impedance_estimate_ohm"] = feat_df["impedance_estimate_ohm"].clip(0.0, 10000.0)

        # 3. Voltage Deviation in Per-Unit (pu)
        # Use each station's own nominal voltage (e.g. GS-05 is a 33 kV hub, others 11 kV)
        station_nominal = {s["station_id"]: s["nominal_kv"] for s in settings.GRID_STATIONS}
        if "station_id" in feat_df.columns:
            v_nom = feat_df["station_id"].map(station_nominal).fillna(settings.NOMINAL_VOLTAGE_KV)
        else:
            v_nom = settings.NOMINAL_VOLTAGE_KV
        feat_df["voltage_deviation_pu"] = np.abs(feat_df["voltage_kv"] - v_nom) / v_nom

        # 4. Frequency Deviation (Hz)
        f_nom = settings.NOMINAL_FREQUENCY_HZ
        feat_df["frequency_deviation_hz"] = np.abs(feat_df["frequency_hz"] - f_nom)

        # 5. Breaker Tripped Indicator (1 for TRIPPED, 0 for CLOSED/OPEN)
        if "breaker_status" in feat_df.columns:
            feat_df["breaker_is_tripped"] = (feat_df["breaker_status"] == "TRIPPED").astype(float)
        else:
            feat_df["breaker_is_tripped"] = 0.0

        return feat_df

    def transform_single(self, record: Dict[str, Any]) -> np.ndarray:
        """
        Transforms a single telemetry dictionary into a scaled feature vector for real-time ML inference.
        """
        single_df = pd.DataFrame([record])
        feat_df = self.compute_features(single_df)
        X = feat_df[self.ALL_FEATURE_COLS].values
        if self.is_fitted:
            return self.scaler.transform(X)
        return X

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray], pd.DataFrame]:
        """
        Fits StandardScaler on training data and computes transformed feature matrix X and target y.
        """
        feat_df = self.compute_features(df)
        X = feat_df[self.ALL_FEATURE_COLS].values
        self.scaler.fit(X)
        self.is_fitted = True
        X_scaled = self.scaler.transform(X)

        y = None
        if "target_condition" in feat_df.columns:
            y = feat_df["target_condition"].astype(str).to_numpy(dtype=object)

        return X_scaled, y, feat_df

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms pre-engineered DataFrame using fitted scaler."""
        feat_df = self.compute_features(df)
        X = feat_df[self.ALL_FEATURE_COLS].values
        if self.is_fitted:
            return self.scaler.transform(X)
        return X
