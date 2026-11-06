"""
========================================================================================
Power-Grid Fault Big-Data Analytics REST API
Module 9: High-Throughput FastAPI Application
Academic Project: MARUMUDI GEORGE MULLAR | Project Guide: Mr. R. SriRamu
Domain: Big Data Analytics, Data Warehousing & Visualization
========================================================================================
"""
import os
import sys
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from database.db_manager import db_manager
from backend.routes import sensors, faults, stations, analytics, simulation

# Create FastAPI instance with rich metadata for Swagger UI
app = FastAPI(
    title="Power-Grid Fault Big-Data Analytics API",
    description="""
### Real-Time Big-Data Monitoring Pipeline & Machine Learning Analytics Solution
**Student:** MARUMUDI GEORGE MULLAR  
**Project Guide:** Mr. R. SriRamu  
**Domain:** Big Data Analytics, Data Warehousing & Visualization  

This REST API serves power-grid telemetry streams, fault classification predictions,
isolation forest anomaly diagnostics, grid station topology metadata, and streaming controls.
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit and cross-origin clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Sub-Routers
app.include_router(sensors.router)
app.include_router(faults.router)
app.include_router(stations.router)
app.include_router(analytics.router)
app.include_router(simulation.router)


@app.on_event("startup")
def on_startup():
    """Ensure database schema is initialized on server startup."""
    db_manager.initialize_database()
    db_manager.log(
        level="INFO",
        component="FastAPI",
        message="Power-Grid REST API Server successfully started."
    )


@app.get("/health", tags=["System Health"])
def health_check():
    """System health check and diagnostic ping."""
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat(),
        "project": settings.PROJECT_TITLE,
        "version": settings.VERSION,
        "database": "CONNECTED",
        "streaming_mode": settings.STREAMING_MODE
    }


@app.get("/logs", tags=["System Logs"])
def get_logs(limit: int = 50):
    """Retrieve recent system operations and diagnostic logs."""
    return db_manager.get_recent_logs(limit=limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
