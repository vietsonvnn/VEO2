# 🚀 Cài Đặt UI - Quick Guide

## ⚠️ Vấn Đề Python 3.14

Python 3.14 có breaking changes với `audioop` module đã bị remove.
Gradio cần pydub, và pydub cần audioop.

## ✅ Giải Pháp

### Option 1: Sử dụng Python 3.11 hoặc 3.12 (RECOMMENDED)

```bash
# Tạo venv mới với Python 3.12
python3.12 -m venv venv312
source venv312/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Chạy UI
python app.py
```

### Option 2: Cài đặt dependencies thủ công

```bash
source venv/bin/activate

# Core dependencies
pip install playwright google-generativeai python-dotenv pyyaml

# Video processing
pip install moviepy opencv-python

# Web UI - install Gradio with compatibility
pip install "gradio>=4.0,<5.0"

# Utilities
pip install requests aiohttp tqdm

# Playwright browsers
playwright install chromium
```

### Option 3: Chạy UI đơn giản (không dùng Gradio)

Tôi đã tạo file `simple_ui.py` với Flask (lightweight hơn):

```bash
pip install flask
python simple_ui.py
```

## 🎯 Kiểm Tra Cài Đặt

```bash
# Check Python version
python --version

# Check Gradio
python -c "import gradio; print(gradio.__version__)"

# Check Playwright
python -c "import playwright; print('OK')"

# Check tất cả
python quick_test.py
```

## 📋 Dependencies Checklist

- [ ] Python 3.11 or 3.12 (NOT 3.14)
- [ ] playwright >= 1.48.0
- [ ] google-generativeai >= 0.8.3
- [ ] gradio >= 4.0
- [ ] moviepy
- [ ] Chromium browser (via playwright install)

## 🔧 Troubleshooting

### Error: "No module named 'audioop'"
→ Đang dùng Python 3.14
→ Giải pháp: Dùng Python 3.12

### Error: "No module named 'gradio'"
→ Chưa cài gradio
→ Giải pháp: `pip install gradio`

### Error: "Browser not found"
→ Chưa cài Chromium
→ Giải pháp: `playwright install chromium`

## 📞 Support

Nếu vẫn lỗi, check:
- `data/logs/automation.log`
- Python version: `python --version`
- Installed packages: `pip list | grep gradio`
