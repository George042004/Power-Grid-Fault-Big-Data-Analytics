"""
Apache Kafka Configuration and Topic Definitions.
"""
from config.settings import settings

KAFKA_BOOTSTRAP_SERVERS = settings.KAFKA_BOOTSTRAP_SERVERS
TOPIC_TELEMETRY = settings.KAFKA_TOPIC_TELEMETRY
TOPIC_FAULTS = settings.KAFKA_TOPIC_FAULTS
TOPIC_PROCESSED = settings.KAFKA_TOPIC_PROCESSED
CONSUMER_GROUP = settings.KAFKA_CONSUMER_GROUP

DEFAULT_KAFKA_PRODUCER_CONFIG = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "client.id": "powergrid-producer",
    "acks": "all",
    "retries": 3,
    "max.in.flight.requests.per.connection": 1
}

DEFAULT_KAFKA_CONSUMER_CONFIG = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": CONSUMER_GROUP,
    "auto.offset.reset": "latest",
    "enable.auto.commit": True
}
