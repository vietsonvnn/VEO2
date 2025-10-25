#!/bin/bash
# Script to run VEO 3.1 UI with Python 3.12

echo "========================================="
echo "🎬 VEO 3.1 Video Automation UI"
echo "========================================="
echo ""

# Activate Python 3.12 venv
echo "🔧 Activating Python 3.12 environment..."
source venv312/bin/activate

# Check Python version
echo "✅ Python version: $(python --version)"

# Run UI
echo ""
echo "🚀 Starting Gradio UI..."
echo "📍 Access at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================="
echo ""

python app.py
