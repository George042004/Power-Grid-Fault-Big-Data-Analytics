"""
Analytics & Machine Learning Metrics REST Endpoints.
"""
from typing import List, Dict, Any
from fastapi import APIRouter
from database.db_manager import db_manager
from machine_learning.evaluate import ModelEvaluator
from backend.schemas import AnalyticsSummarySchema, FaultDistributionItem

router = APIRouter(prefix="", tags=["Analytics & Model Metrics"])


@router.get("/analytics/summary", response_model=AnalyticsSummarySchema)
def get_analytics_summary():
    """Retrieve high-level summary KPIs (readings, faults, anomalies, health score)."""
    return db_manager.get_analytics_summary()


@router.get("/analytics/fault-distribution", response_model=List[FaultDistributionItem])
def get_fault_distribution():
    """Retrieve frequency breakdown of faults by category."""
    return db_manager.get_fault_distribution()


@router.get("/model/metrics")
def get_model_metrics():
    """Retrieve machine learning evaluation metrics (accuracy, precision, recall, F1, confusion matrix)."""
    return ModelEvaluator.get_summary_report()
