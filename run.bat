@echo off
title SmartOMR Launcher
echo ==============================================================================
echo                      SmartOMR Evaluation System
echo          AI-Powered Bulk OMR Sheet Evaluation & Grading Platform
echo ==============================================================================
echo.

echo [1/2] Launching Backend API (FastAPI on http://localhost:8000)...
start "SmartOMR Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Frontend Interface (Next.js on http://localhost:3000)...
start "SmartOMR Frontend UI" cmd /k "cd frontend && npm run dev"

echo.
echo ==============================================================================
echo All services are launching!
echo.
echo   - Frontend Portal:    http://localhost:3000
echo   - Backend API Docs:   http://localhost:8000/docs
echo   - Default Teacher:    teacher@smartomr.com
echo   - Default Password:   Teacher@123
echo ==============================================================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 >nul
start http://localhost:3000
