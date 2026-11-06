"""
Model Evaluation and Diagnostic Metrics Analysis.
"""
import os
import sys
import json
import joblib
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings


class ModelEvaluator:
    """Provides methods to load and inspect evaluation results and model metrics."""

    @staticmethod
    def load_classifier_metrics() -> Optional[Dict[str, Any]]:
        path = settings.MODELS_DIR / "classifier_metrics.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_anomaly_metrics() -> Optional[Dict[str, Any]]:
        path = settings.MODELS_DIR / "anomaly_metrics.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_summary_report() -> Dict[str, Any]:
        cls_metrics = ModelEvaluator.load_classifier_metrics() or {}
        ano_metrics = ModelEvaluator.load_anomaly_metrics() or {}
        return {
            "classifier": {
                "accuracy": cls_metrics.get("accuracy", 0.0),
                "precision": cls_metrics.get("precision", 0.0),
                "recall": cls_metrics.get("recall", 0.0),
                "f1_score": cls_metrics.get("f1_score", 0.0),
                "classes": cls_metrics.get("classes", []),
                "confusion_matrix": cls_metrics.get("confusion_matrix", []),
                "feature_importances": cls_metrics.get("feature_importances", {})
            },
            "anomaly_detector": {
                "total_samples": ano_metrics.get("total_samples", 0),
                "anomaly_samples": ano_metrics.get("anomaly_samples", 0),
                "anomaly_rate": ano_metrics.get("anomaly_rate", 0.0),
                "contamination": ano_metrics.get("hyperparameters", {}).get("contamination", 0.1)
            }
        }
