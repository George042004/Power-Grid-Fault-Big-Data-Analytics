"""
Simulation & Streaming Control REST Endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from streaming.local_stream import local_stream_manager
from backend.schemas import SimulationControlRequest, FaultInjectionRequest

router = APIRouter(prefix="/simulation", tags=["Simulation & Streaming Control"])


@router.post("/start")
def start_simulation(payload: SimulationControlRequest):
    """Starts the real-time background sensor generator and streaming pipeline."""
    success = local_stream_manager.start(interval_sec=payload.interval_sec)
    if payload.fault_probability is not None:
        local_stream_manager.fault_probability = payload.fault_probability
    return {
        "status": "success" if success else "failed",
        "message": f"Simulation streaming active (interval: {local_stream_manager.interval_sec}s)",
        "stats": local_stream_manager.get_stats()
    }


@router.post("/stop")
def stop_simulation():
    """Stops the real-time streaming pipeline."""
    local_stream_manager.stop()
    return {
        "status": "success",
        "message": "Simulation streaming halted",
        "stats": local_stream_manager.get_stats()
    }


@router.get("/status")
def get_simulation_status():
    """Retrieves live streaming throughput and telemetry counter statistics."""
    return local_stream_manager.get_stats()


@router.post("/inject-fault")
def inject_fault(payload: FaultInjectionRequest):
    """Schedules an on-demand fault injection into the next live stream cycle."""
    success = local_stream_manager.inject_fault(payload.fault_type)
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid fault type: {payload.fault_type}")
    return {
        "status": "success",
        "message": f"Injected fault scheduled: {payload.fault_type}"
    }
