"""
========================================================================================
Real-Time Inference Engine
Multi-Model Fault Prediction, Anomaly Scoring & Topological Localization
Academic Project: MARUMUDI GEORGE MULLAR | Project Guide: Mr. R. SriRamu
========================================================================================
"""
import os
import sys
import joblib
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from preprocessing.clean_data import DataCleaner
from preprocessing.feature_engineering import FeatureEngineer
from localization.fault_localizer import FaultLocalizer


class GridPredictor:
    """
    Unified inference pipeline combining Random Forest Classifier,
    Isolation Forest Anomaly Detector, and Topological Fault Localizer.
    """

    def __init__(self):
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
        self.localizer = FaultLocalizer()

        self.classifier_bundle = None
        self.anomaly_bundle = None
        self._load_models()

    def _load_models(self) -> None:
        """Loads trained model artifacts if present on disk."""
        cls_path = settings.MODELS_DIR / "fault_classifier.joblib"
        ano_path = settings.MODELS_DIR / "isolation_forest.joblib"

        if cls_path.exists():
            try:
                self.classifier_bundle = joblib.load(cls_path)
            except Exception as e:
                print(f"[GridPredictor Warning] Could not load classifier: {e}")

        if ano_path.exists():
            try:
                self.anomaly_bundle = joblib.load(ano_path)
            except Exception as e:
                print(f"[GridPredictor Warning] Could not load anomaly detector: {e}")

    def reload(self) -> None:
        """Forces reloading of saved model bundles from disk."""
        self._load_models()

    def _rule_based_fallback(self, rec: Dict[str, Any]) -> str:
        """Electrical physics heuristics fallback if model not yet trained."""
        nominal = next((s["nominal_kv"] for s in settings.GRID_STATIONS
                        if s["station_id"] == rec.get("station_id")), 11.0)
        v = rec.get("voltage_kv", nominal) * (11.0 / nominal)  # normalise to 11 kV scale
        i = rec.get("current_a", 180.0)
        f = rec.get("frequency_hz", 50.0)
        temp = rec.get("temperature_c", 45.0)

        if i > 1000.0 or v < 5.0:
            return "Short Circuit"
        elif i > 350.0:
            return "Overload"
        elif temp > 85.0:
            return "Overheating"
        elif v < 9.5:
            return "Voltage Sag"
        elif v > 12.5:
            return "Voltage Swell"
        elif f < 49.3 or f > 50.7:
            return "Frequency Anomaly"
        return "Normal"

    def predict_single(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single raw telemetry reading:
        1. Validates and cleans inputs
        2. Computes electrical features
        3. Classifies fault type & confidence with Random Forest
        4. Computes anomaly score with Isolation Forest
        5. Localizes fault & compiles recommended action
        """
        # 1. Validation & sanitization
        _, clean_rec, _ = self.cleaner.validate_reading_dict(telemetry)

        # 2. Compute features
        single_df = pd.DataFrame([clean_rec])
        feat_df = self.feature_engineer.compute_features(single_df)
        X_raw = feat_df[self.feature_engineer.ALL_FEATURE_COLS].values

        predicted_fault = "Normal"
        confidence = 0.95
        anomaly_score = 0.15
        is_anomaly = False

        # 3. Fault Classification Inference
        if self.classifier_bundle is not None:
            try:
                scaler = self.classifier_bundle["scaler"]
                clf = self.classifier_bundle["model"]
                X_scaled = scaler.transform(X_raw)

                pred_class = clf.predict(X_scaled)[0]
                proba = clf.predict_proba(X_scaled)[0]
                class_idx = list(clf.classes_).index(pred_class)
                conf = float(proba[class_idx])

                predicted_fault = str(pred_class)
                confidence = conf
            except Exception as e:
                predicted_fault = self._rule_based_fallback(clean_rec)
                confidence = 0.85
        else:
            predicted_fault = self._rule_based_fallback(clean_rec)
            confidence = 0.85

        # 4. Anomaly Detection Inference
        if self.anomaly_bundle is not None:
            try:
                ano_scaler = self.anomaly_bundle["scaler"]
                iso_forest = self.anomaly_bundle["model"]
                X_ano_scaled = ano_scaler.transform(X_raw)

                raw_ano = iso_forest.predict(X_ano_scaled)[0]  # -1 anomaly, 1 inlier
                score = float(iso_forest.decision_function(X_ano_scaled)[0])
                anomaly_score = score
                is_anomaly = bool(raw_ano == -1 or predicted_fault != "Normal")
            except Exception:
                is_anomaly = bool(predicted_fault != "Normal")
                anomaly_score = -0.1 if is_anomaly else 0.15
        else:
            is_anomaly = bool(predicted_fault != "Normal")
            anomaly_score = -0.1 if is_anomaly else 0.15

        # 5. Fault Localization & Maintenance Guidance
        station_id = clean_rec.get("station_id", "GS-01")
        feeder_id = clean_rec.get("feeder_id", "FEEDER-A")
        sensor_id = clean_rec.get("sensor_id", "SNS-GS01-A-01")
        ts = clean_rec.get("timestamp", datetime.utcnow().isoformat())

        loc_result = self.localizer.localize(
            predicted_fault=predicted_fault,
            confidence=confidence,
            station_id=station_id,
            feeder_id=feeder_id,
            sensor_id=sensor_id,
            telemetry=clean_rec,
            timestamp=ts
        )

        return {
            "sensor_id": sensor_id,
            "station_id": station_id,
            "feeder_id": feeder_id,
            "timestamp": ts,
            "predicted_fault": predicted_fault,
            "confidence": round(float(confidence), 4),
            "severity": loc_result["severity"],
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(anomaly_score), 4),
            "localization_path": loc_result["localization_path"],
            "recommended_action": loc_result["recommended_action"],
            "cleaned_telemetry": clean_rec
        }


predictor = GridPredictor()
