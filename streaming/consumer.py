"""
Apache Kafka Consumer for Power-Grid Telemetry.
Performs streaming message validation, deduplication, inference, and database persistence.
"""
import json
import time
from typing import Dict, Any, Optional
from collections import deque
from config.settings import settings
from streaming.kafka_config import (
    KAFKA_BOOTSTRAP_SERVERS, TOPIC_TELEMETRY, CONSUMER_GROUP
)
from preprocessing.clean_data import DataCleaner
from machine_learning.predict import predictor
from database.db_manager import db_manager

try:
    from kafka import KafkaConsumer as KafkaPythonConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


class GridKafkaConsumer:
    """Consumes telemetry messages from Kafka and pipelines them into analytics & storage."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
        self.cleaner = DataCleaner()
        self.consumer = None
        self.is_running = False

        # Sliding window hash cache for duplicate detection (last 5000 message fingerprints)
        self.dedup_cache = deque(maxlen=5000)

        if KAFKA_AVAILABLE:
            try:
                self.consumer = KafkaPythonConsumer(
                    TOPIC_TELEMETRY,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=CONSUMER_GROUP,
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    consumer_timeout_ms=1000
                )
                print(f"[KafkaConsumer] Subscribed to topic '{TOPIC_TELEMETRY}'")
            except Exception as e:
                print(f"[KafkaConsumer Notice] Kafka broker unavailable at {self.bootstrap_servers}: {e}")
                self.consumer = None

    def _is_duplicate(self, record: Dict[str, Any]) -> bool:
        """Computes message fingerprint to filter duplicate stream transmissions."""
        sensor_id = record.get("sensor_id", "")
        ts = record.get("timestamp", "")
        v = record.get("voltage_kv", 0.0)
        i = record.get("current_a", 0.0)
        fingerprint = f"{sensor_id}|{ts}|{v:.2f}|{i:.1f}"

        if fingerprint in self.dedup_cache:
            return True
        self.dedup_cache.append(fingerprint)
        return False

    def process_message(self, raw_telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executes streaming pipeline for one message:
        1. Duplicate check
        2. Message validation & missing value imputation
        3. Real-time ML inference (Fault Classifier + Isolation Forest + Localization)
        4. Database persistence
        """
        # 1. Duplicate detection
        if self._is_duplicate(raw_telemetry):
            return None

        # 2. Validation & cleaning
        _, clean_telemetry, _ = self.cleaner.validate_reading_dict(raw_telemetry)

        # 3. Insert sensor reading to DB
        saved_reading = db_manager.insert_sensor_reading(clean_telemetry)
        reading_id = saved_reading.id if saved_reading else None

        # 4. Machine learning prediction & localization
        pred_result = predictor.predict_single(clean_telemetry)

        # 5. Insert fault prediction to DB
        fault_payload = {
            "reading_id": reading_id,
            "sensor_id": clean_telemetry["sensor_id"],
            "station_id": clean_telemetry["station_id"],
            "feeder_id": clean_telemetry["feeder_id"],
            "timestamp": clean_telemetry.get("timestamp"),
            "predicted_fault": pred_result["predicted_fault"],
            "confidence": pred_result["confidence"],
            "severity": pred_result["severity"],
            "localization_path": pred_result["localization_path"],
            "recommended_action": pred_result["recommended_action"]
        }
        db_manager.insert_fault_prediction(fault_payload)

        # 6. Insert anomaly record to DB
        anomaly_payload = {
            "reading_id": reading_id,
            "sensor_id": clean_telemetry["sensor_id"],
            "station_id": clean_telemetry["station_id"],
            "timestamp": clean_telemetry.get("timestamp"),
            "anomaly_score": pred_result["anomaly_score"],
            "is_anomaly": pred_result["is_anomaly"],
            "metric_details": f"Fault: {pred_result['predicted_fault']} (Severity: {pred_result['severity']})"
        }
        db_manager.insert_anomaly_record(anomaly_payload)

        return pred_result

    def start_consuming(self):
        """Starts Kafka polling loop."""
        if not self.consumer:
            print("[KafkaConsumer] Consumer not connected to broker. Exiting consumer loop.")
            return

        self.is_running = True
        print("[KafkaConsumer] Starting Kafka stream consumption...")
        try:
            while self.is_running:
                records = self.consumer.poll(timeout_ms=1000)
                for topic_partition, messages in records.items():
                    for msg in messages:
                        self.process_message(msg.value)
        except Exception as e:
            print(f"[KafkaConsumer Error] Exception in poll loop: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
