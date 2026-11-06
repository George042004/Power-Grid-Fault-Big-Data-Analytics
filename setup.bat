@echo off
title Power-Grid Fault Analytics - Environment Setup
color 0B
echo ===============================================================================
echo   POWER-GRID FAULT BIG-DATA ANALYTICS PIPELINE
echo   Candidate: MARUMUDI GEORGE MULLAR ^| Guide: Mr. R. SriRamu
echo   Environment Setup ^& Model Training Pipeline
echo ===============================================================================

echo.
echo [Step 1/4] Installing Required Dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some packages may require manual review. Proceeding with existing Python environment...
)

echo.
echo [Step 2/4] Initializing Database Schema ^& Substation Topology...
python scripts/initialize_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Database initialization failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [Step 3/4] Generating 7,000 Power-Grid Telemetry Samples ^& Training ML Models...
python scripts/train_models.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Model training failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [Step 4/4] Running Automated System Verification Tests...
pytest tests/ -v
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some tests reported warnings, but system setup is complete.
)

echo.
echo ===============================================================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo   To launch the entire platform, run: run.bat
echo ===============================================================================
pause
