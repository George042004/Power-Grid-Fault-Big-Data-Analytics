"""
Data Cleaning & Quality Pipeline.
Handles duplicates, missing values, physically invalid readings, and outlier clipping.
"""
import os
import sys
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings


class DataCleaner:
    """
    Cleans raw power-grid sensor telemetry records and enforces physical bounds.
    """

    # Physical valid operational ranges for 11kV distribution grid telemetry
    VALID_BOUNDS = {
        "voltage_kv": (0.5, 60.0),           # Covers 11 kV and 33 kV substations incl. swell surges
        "current_a": (0.0, 5000.0),          # Non-negative, bounded below extreme arc-flash
        "frequency_hz": (40.0, 60.0),        # Within ±10 Hz boundary of grid synchronous freq
        "active_power_kw": (-1000.0, 50000.0),
        "reactive_power_kvar": (-20000.0, 50000.0),
        "power_factor": (-1.0, 1.0),
        "temperature_c": (-20.0, 160.0),     # Physical limits of outdoor transformer oils
        "load_pct": (0.0, 500.0),
    }

    def __init__(self):
        self.median_impute_values: Dict[str, float] = {
            "voltage_kv": 11.0,
            "current_a": 180.0,
            "frequency_hz": 50.0,
            "active_power_kw": 3200.0,
            "reactive_power_kvar": 1000.0,
            "power_factor": 0.95,
            "temperature_c": 45.0,
            "load_pct": 60.0
        }

    def validate_reading_dict(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validates and sanitizes a single streaming record in real-time.
        Returns: (is_valid, sanitized_record, reason)
        """
        sanitized = dict(record)

        for col, (low, high) in self.VALID_BOUNDS.items():
            val = sanitized.get(col)
            if val is None or (isinstance(val, (int, float)) and np.isnan(val)):
                # Impute missing value with median fallback
                sanitized[col] = self.median_impute_values.get(col, 0.0)
            else:
                try:
                    fval = float(val)
                    if fval < low or fval > high:
                        # Out of physical bound: clip value to bound edge
                        sanitized[col] = float(np.clip(fval, low, high))
                    else:
                        sanitized[col] = fval
                except (ValueError, TypeError):
                    sanitized[col] = self.median_impute_values.get(col, 0.0)

        # Standardize breaker status
        status = str(sanitized.get("breaker_status", "CLOSED")).upper()
        if status not in ["CLOSED", "OPEN", "TRIPPED"]:
            status = "CLOSED"
        sanitized["breaker_status"] = status
        sanitized["is_valid"] = True

        return True, sanitized, "Passed validation and bound sanitization"

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes complete batch cleaning pipeline on raw telemetry dataset:
        1. Duplicate removal
        2. Missing value imputation
        3. Physical validity checks & outlier clipping
        """
        clean_df = df.copy()

        # 1. Deduplication based on sensor_id and timestamp
        initial_count = len(clean_df)
        if "sensor_id" in clean_df.columns and "timestamp" in clean_df.columns:
            clean_df = clean_df.drop_duplicates(subset=["sensor_id", "timestamp"], keep="first")
            dups_removed = initial_count - len(clean_df)
            if dups_removed > 0:
                print(f"[DataCleaner] Removed {dups_removed} duplicate records.")

        # 2. Impute missing numerical values with column medians
        numerical_cols = [c for c in self.VALID_BOUNDS.keys() if c in clean_df.columns]
        for col in numerical_cols:
            median_val = clean_df[col].median()
            if pd.isna(median_val):
                median_val = self.median_impute_values.get(col, 0.0)
            self.median_impute_values[col] = float(median_val)
            clean_df[col] = clean_df[col].fillna(median_val)

        # 3. Clip values within physical feasibility bounds
        for col, (low, high) in self.VALID_BOUNDS.items():
            if col in clean_df.columns:
                clean_df[col] = clean_df[col].clip(lower=low, upper=high)

        # 4. Standardize text columns
        if "breaker_status" in clean_df.columns:
            clean_df["breaker_status"] = clean_df["breaker_status"].astype(str).str.upper().fillna("CLOSED")

        clean_df["is_valid"] = True
        return clean_df.reset_index(drop=True)
