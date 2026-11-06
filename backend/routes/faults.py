"""
Fault Monitoring & Predictions REST Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Query
from database.db_manager import db_manager
from backend.schemas import FaultPredictionSchema

router = APIRouter(prefix="/faults", tags=["Fault Detection & Diagnostics"])


@router.get("", response_model=List[FaultPredictionSchema])
def get_fault_predictions(
    limit: int = Query(default=50, ge=1, le=500),
    station_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None, description="Filter by NORMAL, WARNING, CRITICAL"),
    fault_type: Optional[str] = Query(default=None)
):
    """Retrieve detected fault prediction records with optional filters."""
    return db_manager.get_recent_faults(
        limit=limit,
        station_id=station_id,
        severity=severity,
        fault_type=fault_type
    )


@router.get("/latest", response_model=List[FaultPredictionSchema])
def get_latest_faults(
    limit: int = Query(default=10, ge=1, le=50)
):
    """Retrieve the most recent fault incidents."""
    return db_manager.get_recent_faults(limit=limit, exclude_normal=True)
