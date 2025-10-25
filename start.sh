#!/bin/bash

echo "=========================================="
echo "🎬 VEO 3.1 Auto UI"
echo "Tự động hoàn toàn - 1 nút tạo video"
echo "=========================================="
echo ""

# Activate virtual environment
source venv312/bin/activate

# Show info
echo "✅ Python: $(python --version)"
echo "✅ API Key: Configured"
echo "✅ Gradio: 5.49.1"
echo ""

# Launch
echo "🚀 Starting Auto UI..."
echo "📍 URL: http://localhost:7860"
echo ""
echo "💡 Quy trình:"
echo "   1. Nhập chủ đề"
echo "   2. Nhấn 'Bắt đầu tạo video tự động'"
echo "   3. Đợi 10-15 phút"
echo "   4. Done!"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python app_auto.py
