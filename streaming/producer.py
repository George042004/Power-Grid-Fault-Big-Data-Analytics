"""
Apache Kafka Producer for Power-Grid Sensor Telemetry.
Handles serialization, buffering, and publication to Kafka topics.
"""
import json
import time
from typing import Dict, Any, Optional
from config.settings import settings
from streaming.kafka_config import (
    KAFKA_BOOTSTRAP_SERVERS, TOPIC_TELEMETRY, TOPIC_FAULTS, TOPIC_PROCESSED
)

try:
    from kafka import KafkaProducer as KafkaPythonProducer
    KAFKA_AVAILABLE = True
except ImportError:
    try:
        from confluent_kafka import Producer as ConfluentProducer
        KAFKA_AVAILABLE = True
    except ImportError:
        KAFKA_AVAILABLE = False


class GridKafkaProducer:
    """Publishes telemetry and alert messages to Apache Kafka."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
        self.producer = None
        self.is_connected = False

        if KAFKA_AVAILABLE:
            try:
                self.producer = KafkaPythonProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    acks="all",
                    retries=3,
                    request_timeout_ms=5000
                )
                self.is_connected = True
                print(f"[KafkaProducer] Connected to Kafka brokers at {self.bootstrap_servers}")
            except Exception as e:
                print(f"[KafkaProducer Notice] Kafka broker unavailable at {self.bootstrap_servers}: {e}")
                print("[KafkaProducer] Note: Local streaming mode is active and fully functional without Kafka.")
                self.is_connected = False
        else:
            print("[KafkaProducer Notice] kafka-python package not installed. Local streaming mode will be used.")

    def send_telemetry(self, telemetry: Dict[str, Any]) -> bool:
        """Publishes raw sensor telemetry to powergrid.sensor.telemetry topic."""
        if not self.is_connected or self.producer is None:
            return False
        try:
            self.producer.send(TOPIC_TELEMETRY, value=telemetry)
            return True
        except Exception as e:
            print(f"[KafkaProducer Error] Failed to publish telemetry: {e}")
            return False

    def send_fault_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Publishes detected fault alert to powergrid.fault.monitoring topic."""
        if not self.is_connected or self.producer is None:
            return False
        try:
            self.producer.send(TOPIC_FAULTS, value=alert_data)
            return True
        except Exception as e:
            print(f"[KafkaProducer Error] Failed to publish fault alert: {e}")
            return False

    def send_processed(self, processed_data: Dict[str, Any]) -> bool:
        """Publishes validated and enriched data to powergrid.processed.data topic."""
        if not self.is_connected or self.producer is None:
            return False
        try:
            self.producer.send(TOPIC_PROCESSED, value=processed_data)
            return True
        except Exception as e:
            print(f"[KafkaProducer Error] Failed to publish processed record: {e}")
            return False

    def flush(self):
        if self.producer:
            self.producer.flush()

    def close(self):
        if self.producer:
            self.producer.close()
