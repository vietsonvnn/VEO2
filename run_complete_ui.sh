#!/bin/bash

echo "=========================================="
echo "🎬 VEO 3.1 Complete Automation System"
echo "=========================================="
echo ""
echo "Hệ thống tự động hóa hoàn chỉnh:"
echo "  ✅ Khởi tạo dự án"
echo "  ✅ Tạo kịch bản tự động"
echo "  ✅ Tạo nội dung SEO"
echo "  ✅ Sinh video AI"
echo "  ✅ Xem trước & phê duyệt"
echo "  ✅ Tải video hàng loạt (Auto-upscale 1080p)"
echo "  ✅ Nối video hoàn chỉnh"
echo ""
echo "=========================================="
echo ""

# Activate virtual environment
source venv312/bin/activate

# Show Python version
echo "🐍 Python version: $(python --version)"
echo ""

# Launch app
echo "🚀 Launching UI..."
echo "📍 URL: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python app_complete.py
