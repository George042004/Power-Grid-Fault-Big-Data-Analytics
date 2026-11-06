"""
Grid Stations REST Endpoints.
"""
from typing import List
from fastapi import APIRouter
from database.db_manager import db_manager
from backend.schemas import GridStationSchema

router = APIRouter(prefix="/stations", tags=["Grid Stations"])


@router.get("", response_model=List[GridStationSchema])
def get_grid_stations():
    """Retrieve all monitored grid substations with geographical and operational metadata."""
    return db_manager.get_all_stations()
