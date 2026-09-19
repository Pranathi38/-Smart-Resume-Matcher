@echo off
REM Smart Resume Matcher - Quick Start Script
REM This script starts both backend and frontend

echo.
echo ========================================
echo Smart Resume Matcher - Quick Start
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with GOOGLE_API_KEY
    echo Copy .env.example to .env and add your API key
    pause
    exit /b 1
)

REM Check if virtual environment exists (reuse venv_resume if present)
if exist "venv_resume\Scripts\activate.bat" (
    set VENV_DIR=venv_resume
) else (
    set VENV_DIR=venv
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    set VENV_DIR=venv
)

REM Activate virtual environment
echo Activating Python virtual environment...
call %VENV_DIR%\Scripts\activate.bat

REM Install dependencies if needed
echo Checking Python dependencies...
pip install -q -r requirements.txt

REM Start backend in new window
echo Starting backend server...
start "Smart Resume Matcher - Backend" cmd /k "python server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Navigate to frontend and start it
echo Starting frontend server...
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install
)

REM Start frontend
start "Smart Resume Matcher - Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Servers starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to close this window...
pause
