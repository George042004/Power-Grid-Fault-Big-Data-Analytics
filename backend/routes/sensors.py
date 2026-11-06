"""
Sensors & Telemetry REST Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from database.db_manager import db_manager
from backend.schemas import SensorReadingSchema

router = APIRouter(prefix="/sensors", tags=["Sensors & Telemetry"])


@router.get("", response_model=List[SensorReadingSchema])
def get_sensor_readings(
    limit: int = Query(default=50, ge=1, le=500),
    station_id: Optional[str] = Query(default=None, description="Filter by Substation ID (e.g. GS-01)")
):
    """Retrieve historical sensor telemetry readings."""
    return db_manager.get_recent_readings(limit=limit, station_id=station_id)


@router.get("/latest", response_model=List[SensorReadingSchema])
def get_latest_sensor_readings(
    limit: int = Query(default=10, ge=1, le=50)
):
    """Retrieve the most recent real-time telemetry snapshots."""
    return db_manager.get_recent_readings(limit=limit)
