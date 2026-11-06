"""
Database Manager providing structured CRUD operations and analytical queries.
Handles connection pooling, transactions, and robust fallback handling.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from backend.database import engine, SessionLocal, Base
from backend.models import (
    GridStation, SensorReading, FaultPrediction, AnomalyRecord, SystemLog
)
from config.settings import settings


class DatabaseManager:
    """Manages database interactions for the power grid monitoring pipeline."""

    STATUS_WINDOW = 10  # recent predictions per station used to derive its status

    def __init__(self):
        self.engine = engine

    def get_session(self) -> Session:
        """Create and return a new database session."""
        return SessionLocal()

    def initialize_database(self) -> bool:
        """
        Creates all tables if they do not exist and populates initial grid substations.
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            
            with self.get_session() as session:
                # Check if stations exist, if not seed default grid substations
                station_count = session.query(GridStation).count()
                if station_count == 0:
                    for st_data in settings.GRID_STATIONS:
                        station = GridStation(
                            station_id=st_data["station_id"],
                            station_name=st_data["name"],
                            region=st_data["region"],
                            latitude=st_data["lat"],
                            longitude=st_data["lon"],
                            nominal_voltage_kv=st_data["nominal_kv"],
                            capacity_mva=st_data["capacity_mva"],
                            status="OPERATIONAL"
                        )
                        session.add(station)
                    session.commit()
                    
                    self.log(
                        level="INFO",
                        component="DatabaseManager",
                        message=f"Initialized database schema and seeded {len(settings.GRID_STATIONS)} grid stations."
                    )
            return True
        except Exception as e:
            print(f"[DatabaseManager Error] Initialization failed: {e}")
            return False

    def log(self, level: str, component: str, message: str) -> None:
        """Record an entry into system_logs."""
        try:
            with self.get_session() as session:
                entry = SystemLog(
                    timestamp=datetime.utcnow(),
                    level=level.upper(),
                    component=component,
                    message=message
                )
                session.add(entry)
                session.commit()
        except Exception as e:
            print(f"[DatabaseManager Log Error]: {e}")

    def insert_sensor_reading(self, reading_data: Dict[str, Any]) -> Optional[SensorReading]:
        """
        Inserts a single sensor reading into the sensor_readings table.
        """
        try:
            with self.get_session() as session:
                ts = reading_data.get("timestamp")
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        ts = datetime.utcnow()
                elif not isinstance(ts, datetime):
                    ts = datetime.utcnow()

                reading = SensorReading(
                    sensor_id=reading_data["sensor_id"],
                    timestamp=ts,
                    station_id=reading_data["station_id"],
                    feeder_id=reading_data["feeder_id"],
                    voltage_kv=float(reading_data["voltage_kv"]),
                    current_a=float(reading_data["current_a"]),
                    frequency_hz=float(reading_data["frequency_hz"]),
                    active_power_kw=float(reading_data["active_power_kw"]),
                    reactive_power_kvar=float(reading_data["reactive_power_kvar"]),
                    power_factor=float(reading_data["power_factor"]),
                    temperature_c=float(reading_data["temperature_c"]),
                    load_pct=float(reading_data["load_pct"]),
                    breaker_status=reading_data.get("breaker_status", "CLOSED"),
                    is_valid=reading_data.get("is_valid", True)
                )
                session.add(reading)
                session.commit()
                session.refresh(reading)
                return reading
        except Exception as e:
            print(f"[DatabaseManager Error] Insert sensor reading failed: {e}")
            return None

    def insert_fault_prediction(self, fault_data: Dict[str, Any]) -> Optional[FaultPrediction]:
        """
        Inserts a fault prediction record.
        """
        try:
            with self.get_session() as session:
                ts = fault_data.get("timestamp")
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        ts = datetime.utcnow()
                elif not isinstance(ts, datetime):
                    ts = datetime.utcnow()

                prediction = FaultPrediction(
                    reading_id=fault_data.get("reading_id"),
                    sensor_id=fault_data["sensor_id"],
                    station_id=fault_data["station_id"],
                    feeder_id=fault_data["feeder_id"],
                    timestamp=ts,
                    predicted_fault=fault_data["predicted_fault"],
                    confidence=float(fault_data["confidence"]),
                    severity=fault_data.get("severity", "WARNING"),
                    localization_path=fault_data.get("localization_path", "UNKNOWN"),
                    recommended_action=fault_data.get("recommended_action", "Inspect Station")
                )
                session.add(prediction)

                # Update substation status from the worst severity in its most recent
                # predictions, so a station recovers once faults clear (no permanent latch).
                session.flush()
                station = session.query(GridStation).filter(GridStation.station_id == prediction.station_id).first()
                if station:
                    recent = (
                        session.query(FaultPrediction.severity)
                        .filter(FaultPrediction.station_id == prediction.station_id)
                        .order_by(desc(FaultPrediction.id))
                        .limit(self.STATUS_WINDOW)
                        .all()
                    )
                    severities = {r[0] for r in recent}
                    if "CRITICAL" in severities:
                        station.status = "CRITICAL"
                    elif "WARNING" in severities:
                        station.status = "WARNING"
                    else:
                        station.status = "OPERATIONAL"

                session.commit()
                session.refresh(prediction)
                return prediction
        except Exception as e:
            print(f"[DatabaseManager Error] Insert fault prediction failed: {e}")
            return None

    def insert_anomaly_record(self, anomaly_data: Dict[str, Any]) -> Optional[AnomalyRecord]:
        """
        Inserts an anomaly detection record.
        """
        try:
            with self.get_session() as session:
                ts = anomaly_data.get("timestamp")
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        ts = datetime.utcnow()
                elif not isinstance(ts, datetime):
                    ts = datetime.utcnow()

                record = AnomalyRecord(
                    reading_id=anomaly_data.get("reading_id"),
                    sensor_id=anomaly_data["sensor_id"],
                    station_id=anomaly_data["station_id"],
                    timestamp=ts,
                    anomaly_score=float(anomaly_data["anomaly_score"]),
                    is_anomaly=bool(anomaly_data.get("is_anomaly", False)),
                    metric_details=anomaly_data.get("metric_details", "")
                )
                session.add(record)
                session.commit()
                session.refresh(record)
                return record
        except Exception as e:
            print(f"[DatabaseManager Error] Insert anomaly record failed: {e}")
            return None

    def get_all_stations(self) -> List[Dict[str, Any]]:
        """Fetch all grid stations with metadata."""
        with self.get_session() as session:
            stations = session.query(GridStation).all()
            return [st.to_dict() for st in stations]

    def get_recent_readings(self, limit: int = 100, station_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch recent sensor telemetry ordered by timestamp descending."""
        with self.get_session() as session:
            query = session.query(SensorReading)
            if station_id and station_id != "ALL":
                query = query.filter(SensorReading.station_id == station_id)
            readings = query.order_by(desc(SensorReading.timestamp)).limit(limit).all()
            return [r.to_dict() for r in readings]

    def get_recent_faults(
        self,
        limit: int = 50,
        station_id: Optional[str] = None,
        severity: Optional[str] = None,
        fault_type: Optional[str] = None,
        exclude_normal: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch recent fault incidents with optional filtering.
        exclude_normal=True hides 'Normal' classifications (alarm feeds)."""
        with self.get_session() as session:
            query = session.query(FaultPrediction)
            if exclude_normal:
                query = query.filter(FaultPrediction.predicted_fault != "Normal")
            if station_id and station_id != "ALL":
                query = query.filter(FaultPrediction.station_id == station_id)
            if severity and severity != "ALL":
                query = query.filter(FaultPrediction.severity == severity)
            if fault_type and fault_type != "ALL":
                query = query.filter(FaultPrediction.predicted_fault == fault_type)
            faults = query.order_by(desc(FaultPrediction.timestamp)).limit(limit).all()
            return [f.to_dict() for f in faults]

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Aggregate statistical summary for overview dashboard and API."""
        with self.get_session() as session:
            total_readings = session.query(func.count(SensorReading.id)).scalar() or 0
            total_faults = session.query(func.count(FaultPrediction.id)).filter(
                FaultPrediction.predicted_fault != "Normal"
            ).scalar() or 0
            normal_readings = session.query(func.count(FaultPrediction.id)).filter(
                FaultPrediction.predicted_fault == "Normal"
            ).scalar() or 0
            total_anomalies = session.query(func.count(AnomalyRecord.id)).filter(
                AnomalyRecord.is_anomaly == True
            ).scalar() or 0
            active_stations = session.query(func.count(GridStation.station_id)).scalar() or 0
            critical_faults = session.query(func.count(FaultPrediction.id)).filter(
                FaultPrediction.severity == "CRITICAL"
            ).scalar() or 0
            warning_faults = session.query(func.count(FaultPrediction.id)).filter(
                FaultPrediction.severity == "WARNING"
            ).scalar() or 0

            # Grid health calculation
            # Weighted share of classified readings that are faulty (critical = 1.0, warning = 0.4)
            total_classified = total_faults + normal_readings
            if total_classified > 0:
                penalty = (critical_faults * 1.0 + warning_faults * 0.4) / total_classified * 100.0
                health_score = round(min(100.0, max(0.0, 100.0 - penalty)), 1)
            else:
                health_score = 100.0
            if health_score >= 85.0:
                op_status = "NORMAL"
            elif health_score >= 60.0:
                op_status = "WARNING"
            else:
                op_status = "CRITICAL"

            return {
                "total_readings": total_readings,
                "total_faults": total_faults,
                "normal_readings": normal_readings,
                "total_anomalies": total_anomalies,
                "active_stations": active_stations,
                "critical_faults": critical_faults,
                "warning_faults": warning_faults,
                "health_score": health_score,
                "operational_status": op_status
            }

    def get_fault_distribution(self) -> List[Dict[str, Any]]:
        """Return fault counts grouped by predicted_fault category."""
        with self.get_session() as session:
            results = (
                session.query(
                    FaultPrediction.predicted_fault,
                    func.count(FaultPrediction.id).label("count")
                )
                .group_by(FaultPrediction.predicted_fault)
                .all()
            )
            return [{"fault_type": r[0], "count": r[1]} for r in results]

    def get_station_fault_distribution(self) -> List[Dict[str, Any]]:
        """Return fault distribution grouped by station_id."""
        with self.get_session() as session:
            results = (
                session.query(
                    FaultPrediction.station_id,
                    FaultPrediction.severity,
                    func.count(FaultPrediction.id).label("count")
                )
                .filter(FaultPrediction.predicted_fault != "Normal")
                .group_by(FaultPrediction.station_id, FaultPrediction.severity)
                .all()
            )
            return [{"station_id": r[0], "severity": r[1], "count": r[2]} for r in results]

    def export_readings_to_df(
        self,
        station_id: Optional[str] = None,
        limit: int = 5000
    ) -> pd.DataFrame:
        """Export sensor readings to a pandas DataFrame."""
        with self.get_session() as session:
            query = session.query(SensorReading)
            if station_id and station_id != "ALL":
                query = query.filter(SensorReading.station_id == station_id)
            readings = query.order_by(desc(SensorReading.timestamp)).limit(limit).all()
            data = [r.to_dict() for r in readings]
            return pd.DataFrame(data)

    def export_faults_to_df(
        self,
        station_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 5000
    ) -> pd.DataFrame:
        """Export fault predictions to a pandas DataFrame."""
        with self.get_session() as session:
            query = session.query(FaultPrediction)
            if station_id and station_id != "ALL":
                query = query.filter(FaultPrediction.station_id == station_id)
            if severity and severity != "ALL":
                query = query.filter(FaultPrediction.severity == severity)
            faults = query.order_by(desc(FaultPrediction.timestamp)).limit(limit).all()
            data = [f.to_dict() for f in faults]
            return pd.DataFrame(data)

    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent system operations and monitoring logs."""
        with self.get_session() as session:
            logs = session.query(SystemLog).order_by(desc(SystemLog.timestamp)).limit(limit).all()
            return [l.to_dict() for l in logs]


# Global singleton instance
db_manager = DatabaseManager()

