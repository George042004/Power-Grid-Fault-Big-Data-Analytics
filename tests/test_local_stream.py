"""
Unit tests for Module 2: Local Streaming Manager.
"""
import pytest
import time
from streaming.local_stream import LocalStreamManager


def test_local_stream_manager_lifecycle():
    streamer = LocalStreamManager()
    assert streamer.is_running is False

    stats = streamer.get_stats()
    assert stats["status"] == "STOPPED"

    # Start streamer
    streamer.start(interval_sec=0.2)
    assert streamer.is_running is True

    # Allow brief window for message production
    time.sleep(1.0)

    stats = streamer.get_stats()
    assert stats["status"] == "RUNNING"
    assert stats["messages_produced"] > 0

    # Test fault injection
    success = streamer.inject_fault("Voltage Sag")
    assert success is True

    # Stop streamer
    streamer.stop()
    assert streamer.is_running is False
    assert streamer.get_stats()["status"] == "STOPPED"
