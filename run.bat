@echo off
setlocal enabledelayedexpansion
title AuraCFO Launcher

echo ===================================================
echo             AuraCFO Auto-Setup & Launcher
echo ===================================================

:: 1. Check & Setup Frontend dependencies
if not exist "%~dp0frontend\node_modules" (
    echo [Frontend] First-time setup detected: node_modules missing.
    echo [Frontend] Running npm install...
    cd /d "%~dp0frontend"
    call npm install
    if !errorlevel! neq 0 (
        echo [ERROR] npm install failed. Make sure Node.js is installed on your computer.
        pause
        exit /b 1
    )
    cd /d "%~dp0"
    echo [Frontend] Setup completed successfully!
)

:: 2. Check & Setup Backend Virtual Environment
if not exist "%~dp0backend\.venv\Scripts\python.exe" (
    echo [Backend] First-time setup detected: .venv missing.
    echo [Backend] Creating Python virtual environment...
    python -m venv "%~dp0backend\.venv"
    if !errorlevel! neq 0 (
        echo [ERROR] Python not found or failed to create venv. Make sure Python 3.12+ is installed and on PATH.
        pause
        exit /b 1
    )
    echo [Backend] Installing Python dependencies (this only happens once)...
    "%~dp0backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
    "%~dp0backend\.venv\Scripts\python.exe" -m pip install -e "%~dp0backend"
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
    echo [Backend] Setup completed successfully!
)

:: 3. Launch Services
echo.
echo [1/2] Launching Backend on http://localhost:8000...
start "AuraCFO Backend (FastAPI)" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching Frontend on http://localhost:5173...
start "AuraCFO Frontend (Vite)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===================================================
echo Platform is booting up!
echo Opening browser: http://localhost:5173
echo ===================================================

:: Give servers 3 seconds to spin up, then open browser automatically
timeout /t 3 /nobreak >nul
start http://localhost:5173

pause
