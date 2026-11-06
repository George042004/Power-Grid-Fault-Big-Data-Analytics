"""
========================================================================================
Machine Learning Model Training Pipeline
Academic Project: MARUMUDI GEORGE MULLAR | Project Guide: Mr. R. SriRamu
Trains Random Forest Multi-Class Classifier and Isolation Forest Anomaly Detector.
========================================================================================
"""
import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from scripts.generate_data import PowerGridSensorGenerator
from machine_learning.train_classifier import FaultClassifierTrainer
from machine_learning.anomaly_detection import AnomalyDetectorTrainer


def main():
    print("=" * 80)
    print("POWER-GRID FAULT BIG-DATA ANALYTICS: MODEL TRAINING PIPELINE")
    print("Candidate: MARUMUDI GEORGE MULLAR | Guide: Mr. R. SriRamu")
    print("=" * 80)

    raw_csv = settings.RAW_DATA_DIR / "power_grid_telemetry_raw.csv"

    # Step 1: Ensure raw dataset is present
    if not raw_csv.exists():
        print("[Step 1] Raw dataset not found. Generating 7,000 synthetic records...")
        generator = PowerGridSensorGenerator(random_seed=42)
        df_raw = generator.generate_dataset(n_samples=7000)
        df_raw.to_csv(raw_csv, index=False)
        sample_path = settings.SAMPLE_DATA_DIR / "power_grid_sample.csv"
        df_raw.head(500).to_csv(sample_path, index=False)
        print(f"Generated and saved raw telemetry to {raw_csv}")
    else:
        print(f"[Step 1] Loading existing raw telemetry dataset from {raw_csv}...")
        df_raw = pd.read_csv(raw_csv)
        print(f"Loaded {len(df_raw)} records.")

    # Step 2: Train Random Forest Multi-Class Fault Classifier
    print("\n" + "=" * 80)
    print("[Step 2] Training Random Forest Fault Classifier (7 Operating Conditions)...")
    print("=" * 80)
    classifier_trainer = FaultClassifierTrainer(n_estimators=120, max_depth=15, random_state=42)
    cls_metrics, _ = classifier_trainer.train_and_evaluate(df_raw)

    # Step 3: Train Isolation Forest Anomaly Detector
    print("\n" + "=" * 80)
    print("[Step 3] Training Isolation Forest Anomaly Detector (Unsupervised)...")
    print("=" * 80)
    anomaly_trainer = AnomalyDetectorTrainer(contamination=0.12, n_estimators=100, random_state=42)
    ano_metrics = anomaly_trainer.train_and_evaluate(df_raw)

    print("\n" + "=" * 80)
    print("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Classifier Accuracy:   {cls_metrics['accuracy'] * 100:.2f}%")
    print(f"Classifier F1-Score:   {cls_metrics['f1_score'] * 100:.2f}%")
    print(f"Anomaly Contamination: {ano_metrics['anomaly_rate'] * 100:.2f}%")
    print("Models saved in: machine_learning/models/")
    print("=" * 80)


if __name__ == "__main__":
    main()
