@echo off
title AuraCFO Launcher
echo ===================================================
echo             Starting AuraCFO Platform
echo ===================================================
echo [1/2] Launching Backend on http://localhost:8000...
start "AuraCFO Backend (FastAPI)" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching Frontend on http://localhost:5173...
start "AuraCFO Frontend (Vite)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===================================================
echo Platform is booting up!
echo Open your browser to: http://localhost:5173
echo ===================================================
pause
