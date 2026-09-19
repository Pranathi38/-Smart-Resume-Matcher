#!/bin/bash

# Smart Resume Matcher - Quick Start Script
# This script starts both backend and frontend

echo ""
echo "========================================"
echo "Smart Resume Matcher - Quick Start"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with GOOGLE_API_KEY"
    echo "Copy .env.example to .env and add your API key"
    exit 1
fi

# Check if virtual environment exists (reuse venv_resume if present)
if [ -f "venv_resume/bin/activate" ] || [ -f "venv_resume/Scripts/activate" ]; then
    VENV_DIR="venv_resume"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    VENV_DIR="venv"
fi

# Activate virtual environment
echo "Activating Python virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    source "$VENV_DIR/Scripts/activate"
fi

# Install dependencies if needed
echo "Checking Python dependencies..."
pip install -q -r requirements.txt

# Start backend in background
echo "Starting backend server..."
python server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Navigate to frontend and start it
echo "Starting frontend server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Servers starting..."
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
