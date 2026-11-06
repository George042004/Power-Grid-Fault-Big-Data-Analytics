"""
Unit tests for Module 9: FastAPI Endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api import app
from database.db_manager import db_manager


@pytest.fixture(scope="module")
def client():
    db_manager.initialize_database()
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "project" in data


def test_stations_endpoint(client):
    response = client.get("/stations")
    assert response.status_code == 200
    stations = response.json()
    assert len(stations) >= 5


def test_sensors_endpoint(client):
    response = client.get("/sensors?limit=5")
    assert response.status_code == 200
    readings = response.json()
    assert isinstance(readings, list)


def test_faults_endpoint(client):
    response = client.get("/faults?limit=5")
    assert response.status_code == 200
    faults = response.json()
    assert isinstance(faults, list)


def test_analytics_summary_endpoint(client):
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    summary = response.json()
    assert "total_readings" in summary
    assert "health_score" in summary


def test_model_metrics_endpoint(client):
    response = client.get("/model/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert "classifier" in metrics
    assert "anomaly_detector" in metrics
