"""
========================================================================================
Unsupervised Anomaly Detector
Module 4B: Isolation Forest Anomaly Detection
Academic Project: MARUMUDI GEORGE MULLAR | Project Guide: Mr. R. SriRamu
========================================================================================
"""
import os
import sys
import json
import joblib
from datetime import datetime
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from preprocessing.clean_data import DataCleaner
from preprocessing.feature_engineering import FeatureEngineer


class AnomalyDetectorTrainer:
    """
    Trains and persists an Isolation Forest model for unsupervised grid telemetry anomaly detection.
    """

    def __init__(self, contamination: float = 0.12, n_estimators: int = 120, random_state: int = 42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains Isolation Forest on feature-engineered telemetry.
        Persists artifact (.joblib) and evaluation metadata.
        """
        print("[AnomalyDetector] Sanitizing and cleaning dataset...")
        clean_df = self.cleaner.clean_dataframe(df)

        print("[AnomalyDetector] Engineering electrical features for anomaly detection...")
        X_scaled, _, feat_df = self.feature_engineer.fit_transform(clean_df)

        print(f"[AnomalyDetector] Training Isolation Forest on {len(X_scaled)} records (contamination={self.contamination})...")
        self.model.fit(X_scaled)

        # In Isolation Forest: predict returns -1 for outlier, 1 for inlier
        raw_preds = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)

        n_anomalies = int(np.sum(raw_preds == -1))
        n_normal = int(np.sum(raw_preds == 1))
        anomaly_rate = float(n_anomalies / len(raw_preds))

        metrics = {
            "model_type": "IsolationForest",
            "hyperparameters": {
                "n_estimators": self.n_estimators,
                "contamination": self.contamination,
                "random_state": self.random_state
            },
            "total_samples": len(raw_preds),
            "normal_samples": n_normal,
            "anomaly_samples": n_anomalies,
            "anomaly_rate": round(anomaly_rate, 4),
            "score_mean": round(float(np.mean(scores)), 4),
            "score_min": round(float(np.min(scores)), 4),
            "score_max": round(float(np.max(scores)), 4),
            "trained_at": datetime.utcnow().isoformat()
        }

        # Persist model bundle
        model_bundle = {
            "model": self.model,
            "scaler": self.feature_engineer.scaler,
            "feature_cols": self.feature_engineer.ALL_FEATURE_COLS
        }
        model_path = settings.MODELS_DIR / "isolation_forest.joblib"
        joblib.dump(model_bundle, model_path)
        print(f"[AnomalyDetector] Isolation Forest bundle saved to {model_path}")

        # Persist metrics JSON
        metrics_path = settings.MODELS_DIR / "anomaly_metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)
        print(f"[AnomalyDetector] Anomaly metrics saved to {metrics_path}")

        print(f"Anomaly Detection Training Complete: {n_anomalies} anomalies flagged ({anomaly_rate * 100:.2f}%)")
        return metrics
