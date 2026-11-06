"""
CLI Streaming Simulation Runner.
Continuously runs the local streaming pipeline, producing and consuming grid telemetry.
"""
import os
import sys
import time
import signal

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from streaming.local_stream import local_stream_manager
from database.db_manager import db_manager


def signal_handler(sig, frame):
    print("\n[Simulator] Stopping streaming engine gracefully...")
    local_stream_manager.stop()
    sys.exit(0)


def main():
    print("=" * 75)
    print("POWER-GRID TELEMETRY REAL-TIME STREAMING SIMULATOR")
    print("Academic Project: MARUMUDI GEORGE MULLAR | Guide: Mr. R. SriRamu")
    print("=" * 75)

    db_manager.initialize_database()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    interval = 1.0
    print(f"Starting local streaming pipeline at {interval}s interval...")
    local_stream_manager.start(interval_sec=interval)

    print("Pipeline active. Emitting & consuming real-time telemetry into SQLite.")
    print("Press Ctrl+C to terminate.")

    try:
        while True:
            time.sleep(5)
            stats = local_stream_manager.get_stats()
            print(
                f"[{time.strftime('%H:%M:%S')}] "
                f"Produced: {stats['messages_produced']} | "
                f"Consumed: {stats['messages_consumed']} | "
                f"Faults: {stats['faults_detected']} | "
                f"Anomalies: {stats['anomalies_detected']}"
            )
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
