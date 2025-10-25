# ⚡ Quick Start - VEO 3.1 với Comet

## 🚀 3 bước để chạy

### 1. Activate environment
```bash
cd /Users/macos/Desktop/VEO2
source venv312/bin/activate
```

### 2. Chạy tool
```bash
python RUN_WITH_COMET.py
```

### 3. Mở browser
```
http://localhost:7860
```

## 📝 Sử dụng

1. **Tab "Tạo kịch bản"**
   - Nhập chủ đề
   - Click "Tạo kịch bản"

2. **Tab "Tạo Video"**
   - Click "Bắt đầu sản xuất"
   - Comet browser sẽ tự mở

3. **Quan sát**
   - Xem Comet window
   - Videos tạo trên Flow

## ⚠️ Lưu ý

- ✅ Comet browser sẽ hiển thị (không headless)
- ⚠️ Flow tạo **2 videos**/prompt (x2 setting)
- 💾 Videos lưu trên Flow (download thủ công)

## 📁 Cần có

- `cookie.txt` - Cookies từ Flow
- `.env` - GEMINI_API_KEY

## 🔧 Nếu lỗi

```bash
# Re-export cookies
# Check .env có API key
# Check Comet đã cài: /Applications/Comet.app
```

That's it! 🎉
