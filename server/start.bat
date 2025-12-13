@echo off
REM Fiber Maintenance Analytics - Server Startup Script (Windows)
REM Run this to start the API server

echo ============================================
echo   Fiber Maintenance Analytics - API Server
echo ============================================
echo.

cd /d "%~dp0"

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    if exist ".env.example" (
        copy .env.example .env
        echo Please edit .env with your database credentials
        pause
        exit /b 1
    ) else (
        echo ERROR: No .env.example found. Please create .env manually.
        pause
        exit /b 1
    )
)

REM Create virtual environment if not exists
if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo [2/3] Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo [3/3] Starting API server...
echo.
echo Server running at: http://0.0.0.0:8000
echo API Docs: http://0.0.0.0:8000/docs
echo Press Ctrl+C to stop
echo.

python api_server.py
pause
