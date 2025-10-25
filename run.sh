#!/bin/bash

echo "=========================================="
echo "🎬 VEO 3.1 Simple UI"
echo "Giao diện đơn giản - Dễ sử dụng"
echo "=========================================="
echo ""

# Activate virtual environment
source venv312/bin/activate

# Show Python version
echo "🐍 Python: $(python --version)"
echo "✅ API Key: Đã cấu hình"
echo ""

# Launch app
echo "🚀 Starting UI..."
echo "📍 URL: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python app_simple.py
