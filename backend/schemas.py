"""
Pydantic Schemas for API Request and Response Validation.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GridStationSchema(BaseModel):
    station_id: str
    station_name: str
    region: str
    latitude: float
    longitude: float
    nominal_voltage_kv: float
    capacity_mva: float
    status: str
    created_at: Optional[str] = None


class SensorReadingSchema(BaseModel):
    id: Optional[int] = None
    sensor_id: str
    timestamp: Optional[str] = None
    station_id: str
    feeder_id: str
    voltage_kv: float
    current_a: float
    frequency_hz: float
    active_power_kw: float
    reactive_power_kvar: float
    power_factor: float
    temperature_c: float
    load_pct: float
    breaker_status: str
    is_valid: bool = True
    created_at: Optional[str] = None


class FaultPredictionSchema(BaseModel):
    id: Optional[int] = None
    reading_id: Optional[int] = None
    sensor_id: str
    station_id: str
    feeder_id: str
    timestamp: Optional[str] = None
    predicted_fault: str
    confidence: float
    severity: str
    localization_path: str
    recommended_action: str
    created_at: Optional[str] = None


class AnomalyRecordSchema(BaseModel):
    id: Optional[int] = None
    reading_id: Optional[int] = None
    sensor_id: str
    station_id: str
    timestamp: Optional[str] = None
    anomaly_score: float
    is_anomaly: bool
    metric_details: Optional[str] = None
    created_at: Optional[str] = None


class AnalyticsSummarySchema(BaseModel):
    total_readings: int
    total_faults: int
    normal_readings: int
    total_anomalies: int
    active_stations: int
    critical_faults: int
    warning_faults: int
    health_score: float
    operational_status: str


class FaultDistributionItem(BaseModel):
    fault_type: str
    count: int


class SimulationControlRequest(BaseModel):
    interval_sec: Optional[float] = Field(default=1.0, ge=0.1, le=60.0)
    fault_probability: Optional[float] = Field(default=0.25, ge=0.0, le=1.0)


class FaultInjectionRequest(BaseModel):
    fault_type: str
