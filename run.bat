@echo off
setlocal EnableDelayedExpansion
title AuraCFO Launcher

echo ===================================================
echo             AuraCFO Auto-Setup and Launcher
echo ===================================================

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"
set "BACKEND=%ROOT%backend"

:: 1. Check Frontend dependencies
if not exist "%FRONTEND%\node_modules" (
    echo [Frontend] First-time setup: node_modules missing.
    echo [Frontend] Running npm install...
    cd /d "%FRONTEND%"
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Ensure Node.js is installed on your computer.
        pause
        exit /b 1
    )
    cd /d "%ROOT%"
    echo [Frontend] Setup completed successfully!
)

:: 2. Check Backend Virtual Environment
if not exist "%BACKEND%\.venv\Scripts\python.exe" (
    echo [Backend] First-time setup: Python virtual environment missing.
    echo [Backend] Creating virtual environment...
    python -m venv "%BACKEND%\.venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python 3.11+ is installed.
        pause
        exit /b 1
    )
    echo [Backend] Bootstrapping pip and installing dependencies...
    "%BACKEND%\.venv\Scripts\python.exe" -m ensurepip --default-pip >nul 2>&1
    "%BACKEND%\.venv\Scripts\python.exe" -m pip install --upgrade pip
    "%BACKEND%\.venv\Scripts\python.exe" -m pip install -e "%BACKEND%"
    if errorlevel 1 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
    echo [Backend] Setup completed successfully!
)

:: 3. Launch Services
echo.
echo [1/2] Launching Backend on http://localhost:8000...
start "AuraCFO Backend" /D "%BACKEND%" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching Frontend on http://localhost:5173...
start "AuraCFO Frontend" /D "%FRONTEND%" cmd /k "npm run dev"

echo.
echo ===================================================
echo Platform is booting up!
echo Opening browser: http://localhost:5173
echo ===================================================

ping -n 4 127.0.0.1 >nul
start http://localhost:5173

echo.
echo Servers are running in background terminals.
echo Press any key to close this launcher window...
pause >nul
