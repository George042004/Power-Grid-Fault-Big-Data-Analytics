"""
========================================================================================
Machine Learning Fault Classifier
Module 4A: Random Forest Multi-Class Fault Classification
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from preprocessing.clean_data import DataCleaner
from preprocessing.feature_engineering import FeatureEngineer


class FaultClassifierTrainer:
    """
    Trains and evaluates Random Forest Multi-Class Classifier for power-grid fault diagnostics.
    """

    def __init__(self, n_estimators: int = 150, max_depth: int = 16, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            class_weight="balanced",
            n_jobs=-1
        )
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()

    def train_and_evaluate(self, df: pd.DataFrame) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Runs complete model training lifecycle:
        1. Preprocess & clean dataset
        2. Feature engineering & scaling
        3. Train/test split (80/20 stratified)
        4. Model fit
        5. Quantitative evaluation: accuracy, precision, recall, F1, confusion matrix
        6. Persist model artifact (.joblib) and metrics JSON
        """
        print("[FaultClassifier] Cleaning and preprocessing dataset...")
        clean_df = self.cleaner.clean_dataframe(df)

        print("[FaultClassifier] Engineering domain electrical features...")
        X_scaled, y, feat_df = self.feature_engineer.fit_transform(clean_df)

        if y is None:
            raise ValueError("Dataset does not contain 'target_condition' label column.")

        # Save processed dataset to data/processed
        processed_csv_path = settings.PROCESSED_DATA_DIR / "power_grid_processed.csv"
        feat_df.to_csv(processed_csv_path, index=False)
        print(f"[FaultClassifier] Saved processed dataset to {processed_csv_path}")

        # Train / Test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.20, random_state=self.random_state, stratify=y
        )

        print(f"[FaultClassifier] Training Random Forest Classifier on {len(X_train)} samples...")
        self.model.fit(X_train, y_train)

        print("[FaultClassifier] Evaluating model performance on test set...")
        y_pred = self.model.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        labels = sorted(list(set(y_test)))
        cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()

        feature_importances = {
            col: round(float(imp), 4)
            for col, imp in zip(self.feature_engineer.ALL_FEATURE_COLS, self.model.feature_importances_)
        }
        # Sort feature importances descending
        feature_importances = dict(sorted(feature_importances.items(), key=lambda x: x[1], reverse=True))

        metrics = {
            "model_type": "RandomForestClassifier",
            "hyperparameters": {
                "n_estimators": self.n_estimators,
                "max_depth": self.max_depth,
                "random_state": self.random_state
            },
            "training_samples": len(X_train),
            "testing_samples": len(X_test),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "classes": labels,
            "confusion_matrix": cm,
            "classification_report": report_dict,
            "feature_importances": feature_importances,
            "trained_at": datetime.utcnow().isoformat()
        }

        # Persist model artifact bundle
        model_bundle = {
            "model": self.model,
            "scaler": self.feature_engineer.scaler,
            "feature_cols": self.feature_engineer.ALL_FEATURE_COLS,
            "classes": self.model.classes_.tolist()
        }
        model_path = settings.MODELS_DIR / "fault_classifier.joblib"
        joblib.dump(model_bundle, model_path)
        print(f"[FaultClassifier] Model bundle saved to {model_path}")

        # Persist metrics JSON
        metrics_path = settings.MODELS_DIR / "classifier_metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)
        print(f"[FaultClassifier] Metrics saved to {metrics_path}")

        print(f"\nModel Performance Summary:")
        print(f"Accuracy:  {acc * 100:.2f}%")
        print(f"Precision: {prec * 100:.2f}%")
        print(f"Recall:    {rec * 100:.2f}%")
        print(f"F1-Score:  {f1 * 100:.2f}%")

        return metrics, cm
