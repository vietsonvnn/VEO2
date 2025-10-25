# 🚀 START HERE - VEO 3.1 Tool với Comet

## 📍 Bạn đang ở đây

Tool đã được chuyển đổi hoàn toàn sang **Comet browser** với **Selenium**.

## ⚡ Quick Start (3 bước)

```bash
# 1. Activate environment
cd /Users/macos/Desktop/VEO2
source venv312/bin/activate

# 2. Run tool
python RUN_WITH_COMET.py

# 3. Open browser
# http://localhost:7860
```

## 📖 Tài liệu

### Đọc theo thứ tự:

1. **QUICK_START_COMET.md** ⭐
   - Quick start 3 bước
   - Cách sử dụng cơ bản

2. **HOW_TO_RUN.md** 📖
   - Hướng dẫn chi tiết
   - Troubleshooting
   - Workflow đầy đủ

3. **COMET_COMPLETE_SUMMARY.md** 🔧
   - Technical overview
   - Known issues
   - Performance metrics

4. **FINAL_COMET_SUMMARY.md** ✅
   - What's completed
   - File structure
   - Next steps

## 📦 Files chính

| File | Mô tả | Cách dùng |
|------|-------|-----------|
| **RUN_WITH_COMET.py** | Main tool với UI | `python RUN_WITH_COMET.py` |
| **test_comet_controller.py** | Test Comet | `python test_comet_controller.py` |
| **cookie.txt** | Flow cookies | Export từ browser |
| **.env** | API keys | Tạo với GEMINI_API_KEY |

## 🔧 Technical Stack

- **Browser**: Comet (Chromium-based)
- **Automation**: Selenium + webdriver-manager
- **Script Gen**: Gemini 2.0 Flash
- **Video Gen**: VEO 3.1 (Flow)
- **UI**: Gradio 5.x
- **Python**: 3.12.12

## ⚠️ Known Limitations

1. **x2 Setting**: Flow tạo 2 videos/prompt - chưa tự động đổi được
2. **Auto Download**: Videos lưu trên Flow - download thủ công
3. **Video Assembly**: Chưa tự động ghép videos

## ✅ Checklist

- [ ] Python 3.12.12 activated
- [ ] cookie.txt có và còn hiệu lực
- [ ] .env có GEMINI_API_KEY
- [ ] Comet installed: `/Applications/Comet.app`

## 🎯 Main Command

```bash
python RUN_WITH_COMET.py
```

**URL**: http://localhost:7860

---

**Ready to go!** 🚀
