@echo off
title Power-Grid Fault Analytics - Multi-Service Launcher
color 0A
echo ===============================================================================
echo   POWER-GRID FAULT BIG-DATA ANALYTICS
echo   Launching Real-Time Streaming Platform ^& Control Room
echo ===============================================================================

echo.
echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 (Swagger docs at /docs)...
start "PowerGrid-FastAPI" cmd /k "python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000"

timeout /t 3 >nul

echo [2/3] Starting Background Telemetry Streaming Engine...
start "PowerGrid-StreamSimulator" cmd /k "python scripts/run_simulation.py"

timeout /t 2 >nul

echo [3/3] Launching Streamlit Control-Room Dashboard on http://localhost:8501...
start "PowerGrid-Dashboard" cmd /k "streamlit run app/dashboard.py"

echo.
echo ===============================================================================
echo   ALL SERVICES ARE ACTIVE!
echo   - Streamlit Dashboard: http://localhost:8501
echo   - FastAPI Backend:     http://127.0.0.1:8000
echo   - Interactive API Docs:http://127.0.0.1:8000/docs
echo ===============================================================================
pause
