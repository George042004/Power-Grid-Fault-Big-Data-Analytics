"""
SQLAlchemy ORM models representing the power-grid database entities.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base


class GridStation(Base):
    """Grid Substation information and operational status."""
    __tablename__ = "grid_stations"

    station_id = Column(String(50), primary_key=True, index=True)
    station_name = Column(String(150), nullable=False)
    region = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    nominal_voltage_kv = Column(Float, default=11.0)
    capacity_mva = Column(Float, default=50.0)
    status = Column(String(50), default="OPERATIONAL")  # OPERATIONAL, WARNING, CRITICAL, OFFLINE
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="station", cascade="all, delete-orphan")
    faults = relationship("FaultPrediction", back_populates="station", cascade="all, delete-orphan")
    anomalies = relationship("AnomalyRecord", back_populates="station", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "station_name": self.station_name,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "nominal_voltage_kv": self.nominal_voltage_kv,
            "capacity_mva": self.capacity_mva,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SensorReading(Base):
    """Real-time and historical power-grid telemetry readings."""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    station_id = Column(String(50), ForeignKey("grid_stations.station_id"), nullable=False, index=True)
    feeder_id = Column(String(50), nullable=False, index=True)
    
    # Telemetry metrics
    voltage_kv = Column(Float, nullable=False)
    current_a = Column(Float, nullable=False)
    frequency_hz = Column(Float, nullable=False)
    active_power_kw = Column(Float, nullable=False)
    reactive_power_kvar = Column(Float, nullable=False)
    power_factor = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    load_pct = Column(Float, nullable=False)
    breaker_status = Column(String(20), default="CLOSED")  # CLOSED, OPEN, TRIPPED
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    station = relationship("GridStation", back_populates="readings")
    fault_prediction = relationship("FaultPrediction", uselist=False, back_populates="reading")
    anomaly_record = relationship("AnomalyRecord", uselist=False, back_populates="reading")

    __table_args__ = (
        Index("idx_sensor_station_time", "station_id", "timestamp"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "station_id": self.station_id,
            "feeder_id": self.feeder_id,
            "voltage_kv": round(self.voltage_kv, 3) if self.voltage_kv is not None else None,
            "current_a": round(self.current_a, 2) if self.current_a is not None else None,
            "frequency_hz": round(self.frequency_hz, 3) if self.frequency_hz is not None else None,
            "active_power_kw": round(self.active_power_kw, 2) if self.active_power_kw is not None else None,
            "reactive_power_kvar": round(self.reactive_power_kvar, 2) if self.reactive_power_kvar is not None else None,
            "power_factor": round(self.power_factor, 3) if self.power_factor is not None else None,
            "temperature_c": round(self.temperature_c, 2) if self.temperature_c is not None else None,
            "load_pct": round(self.load_pct, 2) if self.load_pct is not None else None,
            "breaker_status": self.breaker_status,
            "is_valid": self.is_valid,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FaultPrediction(Base):
    """Machine learning fault classification and localization outputs."""
    __tablename__ = "fault_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    reading_id = Column(Integer, ForeignKey("sensor_readings.id"), nullable=True, index=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    station_id = Column(String(50), ForeignKey("grid_stations.station_id"), nullable=False, index=True)
    feeder_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # ML Prediction fields
    predicted_fault = Column(String(50), nullable=False, index=True)  # Normal, Overload, Short Circuit, etc.
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    severity = Column(String(20), nullable=False, index=True)  # NORMAL, WARNING, CRITICAL
    localization_path = Column(String(200), nullable=False)  # GS-01 -> FEEDER-A -> SNS-01
    recommended_action = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reading = relationship("SensorReading", back_populates="fault_prediction")
    station = relationship("GridStation", back_populates="faults")

    def to_dict(self):
        return {
            "id": self.id,
            "reading_id": self.reading_id,
            "sensor_id": self.sensor_id,
            "station_id": self.station_id,
            "feeder_id": self.feeder_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "predicted_fault": self.predicted_fault,
            "confidence": round(self.confidence, 4) if self.confidence is not None else None,
            "severity": self.severity,
            "localization_path": self.localization_path,
            "recommended_action": self.recommended_action,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AnomalyRecord(Base):
    """Unsupervised anomaly detection outputs from Isolation Forest."""
    __tablename__ = "anomaly_records"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    reading_id = Column(Integer, ForeignKey("sensor_readings.id"), nullable=True, index=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    station_id = Column(String(50), ForeignKey("grid_stations.station_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    anomaly_score = Column(Float, nullable=False)  # Lower is more anomalous
    is_anomaly = Column(Boolean, nullable=False, default=False)
    metric_details = Column(Text, nullable=True)  # JSON or text notes of abnormal parameters
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reading = relationship("SensorReading", back_populates="anomaly_record")
    station = relationship("GridStation", back_populates="anomalies")

    def to_dict(self):
        return {
            "id": self.id,
            "reading_id": self.reading_id,
            "sensor_id": self.sensor_id,
            "station_id": self.station_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "anomaly_score": round(self.anomaly_score, 4) if self.anomaly_score is not None else None,
            "is_anomaly": self.is_anomaly,
            "metric_details": self.metric_details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SystemLog(Base):
    """System operations, streaming events, and audit logs."""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), nullable=False, default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    component = Column(String(50), nullable=False)  # Producer, Consumer, Preprocessor, ML, DB, API
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "component": self.component,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
