# 🚀 VEO 3.1 - Quick Start Guide

## ✅ Đã hoàn thành

- ✅ API Key lưu trong `.env` và `api_key.txt`
- ✅ Script Generator tested & working
- ✅ UI Simple đang chạy trên http://localhost:7860
- ✅ Default values đã điền sẵn
- ✅ Gradio upgraded to 5.49.1

---

## 🎯 Khởi chạy NGAY (1 lệnh)

```bash
./run.sh
```

→ Mở browser: **http://localhost:7860**

---

## 📋 Làm theo 4 bước

### 1️⃣ Tab 1: Tạo kịch bản
- Chủ đề đã điền sẵn: "Hướng dẫn nấu món phở..."
- Click **"✨ Tạo kịch bản"**
- Download file `.json`

### 2️⃣ Tab 2: Sinh video
- Upload file kịch bản
- Cookies: `./config/cookies.json`
- Click **"🎬 Tạo tất cả video"**

### 3️⃣ Tab 3: Tải video
- Upload file kịch bản
- Click **"📥 Tải tất cả video"**

### 4️⃣ Tab 4: Nối video
- Nhập thư mục downloads
- Upload file kịch bản
- Click **"🎞️ Nối video"**
- **Done!** 🎉

---

## 📁 3 versions UI

| File | Status | Khuyến nghị |
|------|--------|-------------|
| **app_simple.py** | ✅ **READY** | **⭐ Dùng này!** Đơn giản nhất |
| app_complete.py | ✅ Running | Đầy đủ 7 tabs (phức tạp hơn) |
| app.py | ✅ Stable | Version cũ (3 tabs) |

**Launcher**:
- `./run.sh` → app_simple.py (khuyến nghị)
- `./run_complete_ui.sh` → app_complete.py
- `./run_ui.sh` → app.py

---

## 🔑 API Key (Đã cấu hình)

```
AIzaSyAe6cP63f9NvTZmfSexQ3a6M1GKm0sh1wo
```

Đã lưu vào:
- ✅ `.env`
- ✅ `api_key.txt`

Không cần làm gì thêm!

---

## 🎬 Test Results

### Script Generator ✅
```
✅ ScriptGenerator initialized
✅ Script generated!
Title: Phở Việt Nam - Tinh Hoa Ẩm Thực
Scenes: 3 scenes
Duration: 8s per scene
```

### UI Status ✅
```
✅ Running on http://localhost:7860
✅ Python 3.12.12
✅ Gradio 5.49.1
✅ Default values filled
```

---

## 📚 Documentation

- [README_SIMPLE.md](README_SIMPLE.md) - Hướng dẫn chi tiết Simple UI
- [STATUS.md](STATUS.md) - Trạng thái toàn bộ hệ thống
- [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md) - Guide đầy đủ 7 bước

---

## 💡 Tips

1. **Cookies**: Extract mới trước khi dùng
   ```bash
   python tools/extract_cookies.py
   ```

2. **Test script ngay**: Tab 1 đã có default topic, chỉ cần click "Tạo kịch bản"

3. **Xem video**: Tab 4 có video player để preview

---

## 🛠️ Troubleshooting

**UI không chạy**:
```bash
pkill -f python && ./run.sh
```

**Lỗi cookies**:
```bash
python tools/extract_cookies.py
```

**Lỗi API**:
```bash
cat .env  # Check API key
```

---

## ✨ Ready to go!

```bash
./run.sh
```

**That's it! Simple as 1-2-3-4!** 🎬✨
