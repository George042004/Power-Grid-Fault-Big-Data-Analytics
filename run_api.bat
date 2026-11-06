@echo off
title Power-Grid FastAPI Backend
color 0B
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
pause
