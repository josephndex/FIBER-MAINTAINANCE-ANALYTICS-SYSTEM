#!/bin/bash
# Fiber Maintenance Analytics - Server Startup Script
# Run this to start the API server

echo "============================================"
echo "  Fiber Maintenance Analytics - API Server"
echo "============================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env with your database credentials"
        exit 1
    else
        echo "ERROR: No .env.example found. Please create .env manually."
        exit 1
    fi
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "[2/3] Installing dependencies..."
pip install -r requirements.txt --quiet

# Start the server
echo "[3/3] Starting API server..."
echo ""
echo "Server running at: http://0.0.0.0:8000"
echo "API Docs: http://0.0.0.0:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

python api_server.py
