# 🎬 VEO 3.1 Complete Tool - Hướng dẫn chạy

## 📋 Tổng quan

Tool tự động tạo phim với:
- **Gemini 2.0 Flash**: Tạo kịch bản
- **VEO 3.1**: Tạo videos cho từng cảnh
- **Comet Browser**: Chạy automation (có thể quan sát và debug)

## 🚀 Cách chạy

### 1. Chuẩn bị

```bash
cd /Users/macos/Desktop/VEO2
source venv312/bin/activate
```

### 2. Chạy tool với Comet

```bash
python RUN_WITH_COMET.py
```

### 3. Mở browser

Truy cập: **http://localhost:7860**

## 📖 Sử dụng

### Bước 1: Tạo kịch bản
1. Tab "1️⃣ Tạo kịch bản"
2. Nhập chủ đề (VD: "Làm phở bò truyền thống")
3. Chọn thời lượng: 0.5-3 phút
4. Project ID: Để mặc định hoặc paste ID của bạn
5. Cookie path: `./cookie.txt`
6. Click **"Tạo kịch bản"**

### Bước 2: Tạo videos
1. Tab "2️⃣ Tạo Video (Comet)"
2. Click **"Bắt đầu sản xuất"**
3. **Comet browser sẽ tự động mở**
4. Quan sát quá trình tạo video
5. Đợi hoàn thành

## 🌐 Về Comet Browser

- **Có thể quan sát**: Cửa sổ browser hiển thị trong quá trình chạy
- **Debug dễ dàng**: Inspect page, xem lỗi, check DOM
- **Không headless**: Bạn thấy mọi thứ tool đang làm

## ⚠️ Lưu ý quan trọng

### Về setting x2 (2 videos)
- **Flow mặc định tạo 2 videos** cho mỗi prompt (x2 setting)
- Tool hiện tại **chưa tự động đổi được** thành x1
- Nếu muốn 1 video: **Thay đổi thủ công** trong Flow UI
  - Click vào "x2" → Menu popup → Chọn "1"
  - Hoặc vào Settings → Thay đổi "Câu trả lời đầu ra" = 1

### Về videos
- Videos được tạo **trên Flow** (cloud)
- **Không tự động download** về máy
- Download thủ công từ Flow nếu cần:
  - Vào project trên Flow
  - Click vào video
  - Menu → Download → Chọn quality

## 📁 Files cần có

### 1. cookie.txt
```
Cookies từ Flow (export từ browser)
Vị trí: ./cookie.txt
```

**Cách export cookies:**
1. Mở Chrome/Comet
2. Vào https://labs.google/fx/vi/tools/flow
3. Login
4. F12 → Console → Paste script export cookies
5. Lưu vào `cookie.txt`

### 2. .env
```
GEMINI_API_KEY=your_api_key_here
```

## 🎯 Workflow hoàn chỉnh

```
1. Tạo kịch bản (Gemini)
   ↓
2. Tạo videos (VEO 3.1 + Comet)
   ↓
3. Videos lưu trên Flow
   ↓
4. Download manual (nếu cần)
   ↓
5. Ghép video (future feature)
```

## 🔧 Khắc phục sự cố

### Lỗi cookies
```
❌ Could not load cookies
```
**Giải pháp**: Export lại cookies từ browser

### Lỗi ChromeDriver
```
❌ ChromeDriver version mismatch
```
**Giải pháp**: Script tự động tải đúng version

### Comet không mở
```
❌ Comet browser not found
```
**Giải pháp**:
- Check path: `/Applications/Comet.app/Contents/MacOS/Comet`
- Hoặc dùng Chrome: Đổi trong `flow_controller.py`

### Video không tạo được
```
❌ Video generation failed
```
**Giải pháp**:
1. Xem Comet window để debug
2. Check cookies còn hiệu lực không
3. Check Project ID có đúng không

## 📊 So sánh modes

| Feature | Headless (Chrome) | Visible (Comet) |
|---------|-------------------|-----------------|
| Tốc độ | Nhanh hơn | Bình thường |
| Debug | Khó | Dễ dàng |
| Quan sát | Không | Có |
| Stability | Cao hơn | Bình thường |

**Tool hiện tại dùng**: Comet (để debug)

## 🎬 Ví dụ

### Input
```
Chủ đề: Làm phở bò Việt Nam
Thời lượng: 1 phút
```

### Output
```
✅ Kịch bản: 7-8 cảnh
✅ Videos: Tạo trên Flow (x2 = 14-16 videos)
✅ Có thể preview trên Flow
```

## 📞 Support

Nếu gặp vấn đề:
1. Check Comet window xem lỗi gì
2. Check logs trong UI
3. Check screenshots trong folder (nếu có)

## 🔄 Updates

### Version hiện tại
- ✅ Comet browser integration
- ✅ Script generation
- ✅ Video creation
- ⚠️ x2 setting (chưa tự động đổi được)
- ❌ Auto download (chưa có)
- ❌ Video assembly (chưa có)

### Planned
- [ ] Tự động đổi x2 → x1
- [ ] Auto download videos
- [ ] Video assembly
- [ ] Scene regeneration UI
