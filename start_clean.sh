#!/bin/bash
# Clean Start Script for VEO 3.1 App
# Kills all old processes and starts fresh

echo "============================================================"
echo "🧹 VEO 3.1 - Clean Start Script"
echo "============================================================"

# Step 1: Kill all Python processes
echo ""
echo "Step 1: Cleaning up old Python processes..."
pkill -9 python 2>/dev/null
pkill -9 Python 2>/dev/null
sleep 1
echo "✅ Python processes cleared"

# Step 2: Free port 7860
echo ""
echo "Step 2: Freeing port 7860..."
lsof -ti:7860 | xargs kill -9 2>/dev/null
sleep 1
PORT_CHECK=$(lsof -ti:7860)
if [ -z "$PORT_CHECK" ]; then
    echo "✅ Port 7860 is free"
else
    echo "⚠️  Port 7860 still in use, trying harder..."
    lsof -ti:7860 | xargs kill -9
    sleep 2
fi

# Step 3: Verify environment
echo ""
echo "Step 3: Verifying environment..."

# Check venv exists
if [ ! -d "venv312" ]; then
    echo "❌ venv312 not found!"
    echo "Please create virtual environment first:"
    echo "  python3.12 -m venv venv312"
    exit 1
fi
echo "✅ Virtual environment found"

# Check cookies exist
if [ ! -f "config/cookies.json" ]; then
    echo "⚠️  Warning: config/cookies.json not found"
    echo "You'll need to export cookies from Flow before testing"
fi

# Check .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env not found"
    echo "You'll need API key for script generation"
fi

# Step 4: Activate venv and start app
echo ""
echo "Step 4: Starting VEO 3.1 App..."
echo "============================================================"
echo ""

source venv312/bin/activate
python app.py
