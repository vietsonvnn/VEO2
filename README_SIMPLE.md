# 🎬 VEO 3.1 Simple UI - Hướng dẫn sử dụng

## ✅ Đã test & sẵn sàng

- ✅ API Key: Đã lưu trong `.env`
- ✅ Script Generator: Hoạt động OK
- ✅ UI: Đang chạy trên port 7860
- ✅ Python 3.12 + Gradio 5.49.1

---

## 🚀 Khởi chạy nhanh

```bash
./run.sh
```

Sau đó mở browser: **http://localhost:7860**

---

## 📋 Quy trình 4 bước đơn giản

### Bước 1: Tạo kịch bản

**Tab 1️⃣ - Tạo kịch bản**

- **Chủ đề**: Đã điền sẵn "Hướng dẫn nấu món phở Việt Nam..."
- **Thời lượng**: 40 giây (có thể điều chỉnh 20-120s)
- **Mỗi cảnh**: 8 giây (có thể điều chỉnh 5-15s)

👉 Nhấn nút **"✨ Tạo kịch bản"**

📥 Kết quả:
- File `script_YYYYMMDD_HHMMSS.json` được tạo
- Tải file về để dùng cho bước tiếp theo

---

### Bước 2: Sinh video

**Tab 2️⃣ - Sinh video**

- **Upload file kịch bản** từ Bước 1
- **File cookies**: Mặc định `./config/cookies.json`

👉 Nhấn nút **"🎬 Tạo tất cả video"**

⏳ Quá trình:
- Tự động mở Google Labs Flow
- Tạo video cho từng cảnh
- Hiển thị progress realtime

---

### Bước 3: Tải video

**Tab 3️⃣ - Tải video**

- **Upload file kịch bản** (cùng file từ Bước 1)
- **File cookies**: Mặc định `./config/cookies.json`

👉 Nhấn nút **"📥 Tải tất cả video"**

📥 Kết quả:
- Tải tất cả video về thư mục `./data/downloads/`
- Auto-upscale 1080p (fallback 720p nếu lỗi)

---

### Bước 4: Nối video

**Tab 4️⃣ - Nối video**

- **Thư mục video**: Nhập đường dẫn từ Bước 3 (VD: `./data/downloads/20241025_123456`)
- **Upload file kịch bản**: Cùng file từ Bước 1

👉 Nhấn nút **"🎞️ Nối video"**

🎉 Kết quả:
- Video hoàn chỉnh tại `./data/final/`
- Xem trực tiếp trong UI
- Sẵn sàng upload YouTube!

---

## 📊 Test Results

### ✅ Script Generation Test
```
✅ ScriptGenerator initialized
✅ Script generated!
Title: Phở Việt Nam - Tinh Hoa Ẩm Thực
Scenes: 3
First scene: Cảnh quay cận cảnh nồi nước dùng phở đang sôi nhẹ...
Duration: 8s
```

### ✅ UI Status
- URL: http://localhost:7860
- Status: Running
- Gradio: 5.49.1
- Python: 3.12.12

---

## 🎯 Điểm mạnh của Simple UI

### 1. Đơn giản
- Chỉ 4 tabs, 4 bước
- Không cần cấu hình phức tạp
- Giá trị mặc định sẵn sàng test

### 2. Trực quan
- UI đẹp với theme Soft
- Emoji icons rõ ràng
- Hướng dẫn ngay trong UI

### 3. Hiệu quả
- Workflow tuyến tính: 1 → 2 → 3 → 4
- Không có tính năng thừa
- Focus vào core functionality

---

## 📁 Cấu trúc dữ liệu

```
data/
├── scripts/           # Kịch bản JSON từ Bước 1
│   └── script_20241025_140000.json
├── videos/            # Video tạm từ Bước 2 (optional)
├── downloads/         # Video đã tải từ Bước 3
│   └── 20241025_143000/
│       ├── scene_001_1080p.mp4
│       ├── scene_002_1080p.mp4
│       └── scene_003_720p.mp4
└── final/             # Video hoàn chỉnh từ Bước 4
    └── final_video_20241025_150000.mp4
```

---

## 🔧 Troubleshooting

### Lỗi API key

**Lỗi**: `❌ Chưa có API key`

**Fix**:
```bash
# Kiểm tra .env
cat .env

# Nếu chưa có, tạo lại
echo "GEMINI_API_KEY=AIzaSyAe6cP63f9NvTZmfSexQ3a6M1GKm0sh1wo" > .env
```

### Lỗi cookies

**Lỗi**: `❌ Vui lòng cung cấp file cookies.json`

**Fix**:
```bash
# Extract cookies mới
python tools/extract_cookies.py

# File output: ./config/cookies.json
```

### UI không khởi động

**Fix**:
```bash
# Dừng processes cũ
pkill -f "python.*app"

# Khởi chạy lại
./run.sh
```

---

## 💡 Tips & Best Practices

### 1. Chủ đề tốt

✅ **TỐT**:
- "Hướng dẫn nấu món phở Việt Nam truyền thống"
- "Review chi tiết iPhone 16 Pro Max"
- "Top 5 địa điểm du lịch ở Đà Nẵng"

❌ **KHÔNG TỐT**:
- "Video về ẩm thực"  (quá chung chung)
- "Hướng dẫn"  (thiếu chi tiết)

### 2. Thời lượng hợp lý

- **Short-form** (TikTok, Reels): 20-30s, mỗi cảnh 5-8s
- **YouTube standard**: 40-90s, mỗi cảnh 8-12s
- **YouTube long-form**: 90-120s, mỗi cảnh 10-15s

### 3. Cookies luôn fresh

- Extract cookies mới trước mỗi session
- Google Labs có thể logout sau 24h
- Nếu lỗi auth → Extract lại cookies

---

## 🎬 Demo Workflow

**Ví dụ: Tạo video "Hướng dẫn nấu phở"**

```
1. Tab 1: Tạo kịch bản
   → Chủ đề: "Hướng dẫn nấu món phở..."
   → 40s total, 8s/scene
   → Click "Tạo kịch bản"
   → Download script_20241025_140000.json

2. Tab 2: Sinh video
   → Upload script_20241025_140000.json
   → Cookies: ./config/cookies.json
   → Click "Tạo tất cả video"
   → Đợi 3-5 phút (AI đang tạo)

3. Tab 3: Tải video
   → Upload script_20241025_140000.json
   → Click "Tải tất cả video"
   → Đợi download + upscale

4. Tab 4: Nối video
   → Thư mục: ./data/downloads/20241025_143000
   → Upload script_20241025_140000.json
   → Click "Nối video"
   → ✅ Xong! Video ở ./data/final/
```

**Tổng thời gian**: ~10-15 phút (tùy số cảnh)

---

## 📚 So sánh versions

| Feature | Simple UI | Complete UI | app.py (old) |
|---------|-----------|-------------|--------------|
| Tabs | 4 | 7 | 3 |
| Complexity | ⭐ Easy | ⭐⭐⭐ Advanced | ⭐⭐ Medium |
| Default values | ✅ Yes | ✅ Yes | ❌ No |
| Project management | ❌ No | ✅ Yes | ❌ No |
| SEO generation | ❌ No | ✅ Yes | ❌ No |
| Video preview | ❌ No | ✅ Yes | ❌ No |
| Scene approval | ❌ No | ✅ Yes | ❌ No |
| **Recommended for** | Quick testing | Full production | Development |

---

## ✅ Status

**Version**: 1.0 - Simple & Clean
**Status**: ✅ Ready to use
**Last tested**: 2025-10-25 14:35
**API Key**: ✅ Configured
**UI**: ✅ Running on http://localhost:7860

---

**Happy creating! 🎬✨**

Sử dụng ngay:
```bash
./run.sh
```
