"""
========================================================================================
Local Python Streaming Engine (In-Memory Kafka Alternative)
Module 2: High-Performance Real-Time Streaming Simulator
Academic Project: MARUMUDI GEORGE MULLAR | Project Guide: Mr. R. SriRamu

Allows complete real-time streaming, producer-consumer decoupling, fault injection,
and live analytics without requiring external Apache Kafka broker installation.
========================================================================================
"""
import time
import queue
import threading
from datetime import datetime
from collections import deque
from typing import Dict, Any, Optional, List

from config.settings import settings
from scripts.generate_data import PowerGridSensorGenerator
from preprocessing.clean_data import DataCleaner
from machine_learning.predict import predictor
from database.db_manager import db_manager


class LocalStreamManager:
    """
    Manages in-memory topic queues, background producer thread, and consumer thread.
    Simulates Apache Kafka architecture with zero external daemon dependencies.
    """

    def __init__(self):
        # Thread-safe in-memory topic queues
        self.queue_telemetry = queue.Queue(maxsize=10000)
        self.queue_faults = queue.Queue(maxsize=10000)
        self.queue_processed = queue.Queue(maxsize=10000)

        self.generator = PowerGridSensorGenerator()
        self.cleaner = DataCleaner()

        # State flags
        self.is_running = False
        self._producer_thread = None
        self._consumer_thread = None

        # Streaming parameters
        self.interval_sec = settings.SIMULATION_INTERVAL_SEC
        self.fault_probability = settings.FAULT_INJECTION_PROBABILITY
        self.manual_fault_injection: Optional[str] = None

        # Stream statistics counters
        self.stats = {
            "messages_produced": 0,
            "messages_consumed": 0,
            "duplicates_dropped": 0,
            "faults_detected": 0,
            "anomalies_detected": 0,
            "started_at": None,
            "last_message_at": None,
            "status": "STOPPED"
        }

        # Deduplication cache (last 5000 fingerprints)
        self.dedup_cache = deque(maxlen=5000)
        self._lock = threading.Lock()

    def _is_duplicate(self, record: Dict[str, Any]) -> bool:
        """Sliding window duplicate detector."""
        sensor_id = record.get("sensor_id", "")
        ts = record.get("timestamp", "")
        v = record.get("voltage_kv", 0.0)
        i = record.get("current_a", 0.0)
        fingerprint = f"{sensor_id}|{ts}|{v:.2f}|{i:.1f}"

        with self._lock:
            if fingerprint in self.dedup_cache:
                self.stats["duplicates_dropped"] += 1
                return True
            self.dedup_cache.append(fingerprint)
            return False

    def inject_fault(self, fault_type: str) -> bool:
        """Forces next stream cycle to emit an injected fault condition."""
        if fault_type in settings.FAULT_CLASSES:
            self.manual_fault_injection = fault_type
            db_manager.log(
                level="INFO",
                component="StreamingSimulator",
                message=f"Manual fault injection scheduled: {fault_type}"
            )
            return True
        return False

    def _producer_worker(self):
        """Simulates distributed IoT substation sensors streaming live telemetry."""
        while self.is_running:
            try:
                # Cycle through stations and feeders to emit telemetry
                for st in settings.GRID_STATIONS:
                    if not self.is_running:
                        break

                    for feeder in ["FEEDER-A", "FEEDER-B"]:
                        # Determine operating condition
                        cond = None
                        if self.manual_fault_injection:
                            cond = self.manual_fault_injection
                            self.manual_fault_injection = None
                        elif self.fault_probability > 0:
                            import random
                            if random.random() < self.fault_probability:
                                cond = random.choice(settings.FAULT_CLASSES[1:])
                            else:
                                cond = "Normal"

                        telemetry = self.generator.generate_single_reading(
                            station_id=st["station_id"],
                            feeder_id=feeder,
                            sensor_index=1,
                            condition=cond,
                            timestamp=datetime.utcnow()
                        )

                        # Enqueue to telemetry topic
                        try:
                            self.queue_telemetry.put_nowait(telemetry)
                            with self._lock:
                                self.stats["messages_produced"] += 1
                        except queue.Full:
                            pass

                time.sleep(self.interval_sec)

            except Exception as e:
                print(f"[LocalStream Producer Error]: {e}")
                time.sleep(1.0)

    def _consumer_worker(self):
        """Processes incoming telemetry, runs ML, and persists results."""
        while self.is_running:
            try:
                try:
                    telemetry = self.queue_telemetry.get(timeout=0.5)
                except queue.Empty:
                    continue

                # 1. Deduplication
                if self._is_duplicate(telemetry):
                    self.queue_telemetry.task_done()
                    continue

                # 2. Data Cleaning & bound validation
                _, clean_rec, _ = self.cleaner.validate_reading_dict(telemetry)

                # 3. Insert reading into Database
                saved_reading = db_manager.insert_sensor_reading(clean_rec)
                reading_id = saved_reading.id if saved_reading else None

                # 4. Real-time ML Inference & Localization
                pred_result = predictor.predict_single(clean_rec)

                # 5. Insert Fault Prediction
                fault_payload = {
                    "reading_id": reading_id,
                    "sensor_id": clean_rec["sensor_id"],
                    "station_id": clean_rec["station_id"],
                    "feeder_id": clean_rec["feeder_id"],
                    "timestamp": clean_rec.get("timestamp"),
                    "predicted_fault": pred_result["predicted_fault"],
                    "confidence": pred_result["confidence"],
                    "severity": pred_result["severity"],
                    "localization_path": pred_result["localization_path"],
                    "recommended_action": pred_result["recommended_action"]
                }
                db_manager.insert_fault_prediction(fault_payload)

                # 6. Insert Anomaly Record
                anomaly_payload = {
                    "reading_id": reading_id,
                    "sensor_id": clean_rec["sensor_id"],
                    "station_id": clean_rec["station_id"],
                    "timestamp": clean_rec.get("timestamp"),
                    "anomaly_score": pred_result["anomaly_score"],
                    "is_anomaly": pred_result["is_anomaly"],
                    "metric_details": f"Fault: {pred_result['predicted_fault']}"
                }
                db_manager.insert_anomaly_record(anomaly_payload)

                # 7. Route to Processed & Fault topics
                try:
                    self.queue_processed.put_nowait({
                        "reading": clean_rec,
                        "prediction": pred_result
                    })
                    if pred_result["predicted_fault"] != "Normal":
                        self.queue_faults.put_nowait(pred_result)
                except queue.Full:
                    pass

                # Update live stats
                with self._lock:
                    self.stats["messages_consumed"] += 1
                    self.stats["last_message_at"] = datetime.utcnow().isoformat()
                    if pred_result["predicted_fault"] != "Normal":
                        self.stats["faults_detected"] += 1
                    if pred_result["is_anomaly"]:
                        self.stats["anomalies_detected"] += 1

                self.queue_telemetry.task_done()

            except Exception as e:
                print(f"[LocalStream Consumer Error]: {e}")
                time.sleep(0.5)

    def start(self, interval_sec: Optional[float] = None) -> bool:
        """Starts the local streaming simulation threads."""
        if self.is_running:
            return True

        if interval_sec:
            self.interval_sec = interval_sec

        self.is_running = True
        self.stats["status"] = "RUNNING"
        self.stats["started_at"] = datetime.utcnow().isoformat()

        self._producer_thread = threading.Thread(target=self._producer_worker, daemon=True, name="StreamProducer")
        self._consumer_thread = threading.Thread(target=self._consumer_worker, daemon=True, name="StreamConsumer")

        self._producer_thread.start()
        self._consumer_thread.start()

        db_manager.log(
            level="INFO",
            component="LocalStreamManager",
            message=f"Local stream pipeline started (interval: {self.interval_sec}s)."
        )
        print(f"[LocalStreamManager] Pipeline started successfully (interval: {self.interval_sec}s).")
        return True

    def stop(self) -> bool:
        """Stops the streaming simulation threads."""
        if not self.is_running:
            return True

        self.is_running = False
        self.stats["status"] = "STOPPED"

        db_manager.log(
            level="INFO",
            component="LocalStreamManager",
            message="Local stream pipeline stopped."
        )
        print("[LocalStreamManager] Pipeline stopped.")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Returns current operational status and message throughput statistics."""
        with self._lock:
            stats_copy = dict(self.stats)
            stats_copy["queue_telemetry_size"] = self.queue_telemetry.qsize()
            stats_copy["queue_faults_size"] = self.queue_faults.qsize()
            stats_copy["queue_processed_size"] = self.queue_processed.qsize()
            stats_copy["interval_sec"] = self.interval_sec
            stats_copy["fault_probability"] = self.fault_probability
            return stats_copy


# Singleton instance shared across the application
local_stream_manager = LocalStreamManager()
