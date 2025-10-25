# 📖 Hướng dẫn sử dụng VEO 3.1 Movie Production

## 🚀 Khởi động

```bash
source venv312/bin/activate
python app.py
```

Truy cập: **http://localhost:7860**

---

## 📋 Chuẩn bị

### 1. **Cookie file** (`./cookie.txt`)
- Export cookies từ browser (đã đăng nhập Google)
- Lưu vào file `./cookie.txt`

### 2. **Project ID** (Flow)

Có 2 cách:

#### Option A: Dùng Project ID có sẵn ✅ RECOMMENDED
1. Vào https://labs.google/fx/vi/tools/flow
2. Tạo 1 project mới (hoặc dùng project cũ)
3. Copy Project ID từ URL:
   ```
   https://labs.google/fx/vi/tools/flow/project/abc123def456
                                                ^^^^^^^^^^^^^^^^
                                                Project ID này
   ```
4. Paste vào field "📁 Project ID" trong UI

**Ưu điểm**:
- ✅ Không bị lỗi tạo project
- ✅ Tất cả videos được lưu trong 1 project
- ✅ Dễ quản lý

#### Option B: Để trống (tự động tạo mới)
- Tool sẽ thử tạo project mới
- Có thể thất bại nếu Flow API thay đổi
- ⚠️ KHÔNG khuyến khích

---

## 🎬 Workflow sử dụng

### **TAB 1: Tạo video**

#### Bước 1: Nhập thông tin
```
✨ Chủ đề: "Hướng dẫn nấu món phở Việt Nam truyền thống"
⏱️ Thời lượng: 1 phút (slider 0.5 - 3 phút)
🔑 Cookies: ./cookie.txt
📁 Project ID: abc123def456  ← QUAN TRỌNG!
```

#### Bước 2: Tạo kịch bản
1. Click **"📝 Tạo kịch bản"**
2. Gemini AI sẽ tạo script với N scenes (1 phút = 7-8 scenes)
3. Xem kết quả:
   ```
   ✅ Kịch bản đã tạo!

   📝 Phở Việt Nam: Hương Vị Truyền Thống
   🎬 7 cảnh
   ⏱️ 1 phút (60s)

   Nhấn "Tạo tất cả video" để bắt đầu!
   ```

#### Bước 3: Tạo tất cả video
1. Click **"🎬 Tạo tất cả video"**
2. Xem tiến trình:
   ```
   ============================================================
   🎬 BẮT ĐẦU SẢN XUẤT PHIM
   ============================================================
   📝 Kịch bản: Phở Việt Nam: Hương Vị Truyền Thống
   🎞️ Tổng số cảnh: 7
   ⏱️ Thời lượng: 60s
   ============================================================

   🚀 Khởi động browser...
   ✅ Browser đã sẵn sàng
   🌐 Đang vào trang Flow...
   ✅ Đã vào trang Flow
   📁 Sử dụng project có sẵn: abc123def456...
   ✅ Đã vào project

   ────────────────────────────────────────────────────────────
   🎬 SCENE 1/7
   📝 Mô tả: Cận cảnh các nguyên liệu...

      ⏳ Đang tạo video (VEO 3.1)...
      ✅ Video đã tạo xong!
      📥 Đang download (1080p)...
      ✅ Download hoàn tất!
      💾 Lưu tại: scene_001.mp4
      ✨ Scene 1: HOÀN THÀNH

   [... 6 scenes còn lại ...]

   ============================================================
   📊 KẾT QUẢ CUỐI CÙNG
   ============================================================
   ✅ Hoàn thành: 7/7 cảnh
   ============================================================
   🎉 HOÀN THÀNH TOÀN BỘ!
   ============================================================
   ```

3. Browser sẽ:
   - Mở tự động (headless=False → có thể xem)
   - Vào Flow page
   - Vào project
   - Tạo từng video (8s mỗi cái)
   - Download về `./data/projects/[timestamp]/videos/`

---

### **TAB 2: Xem & tạo lại**

#### Preview từng scene
1. Chuyển sang tab **"2️⃣ Xem & tạo lại"**
2. Xem 10 scene slots với video player
3. Click Play để xem từng video

#### Tạo lại scene không đẹp
Nếu Scene 3 không ưng:
1. Click button **"🔄 Tạo lại Scene 3"**
2. Xem log:
   ```
   ============================================================
   🔄 TẠO LẠI SCENE 3
   ============================================================
   📝 Mô tả: Đầu bếp thái thịt bò...

   🚀 Khởi động browser...
   ✅ Browser đã sẵn sàng
   🌐 Đang vào trang Flow...
   ✅ Đã vào trang Flow
   📁 Đang vào project: abc123def456...
   ✅ Đã vào project

   ⏳ Đang tạo video với VEO 3.1...
   ✅ Video đã tạo xong!
   📥 Đang download video (1080p)...
   ✅ Download hoàn tất!
   💾 Lưu tại: scene_003.mp4

   ============================================================
   🎉 Scene 3 đã được tạo lại thành công!
   ============================================================
   ```

3. Video player tự động update với video mới

**Lưu ý**: VEO 3.1 là AI generative → mỗi lần tạo khác nhau, có thể tạo lại nhiều lần đến khi hài lòng

---

### **TAB 3: Video cuối**

#### Ghép phim hoàn chỉnh
1. Chuyển sang tab **"3️⃣ Video cuối"**
2. Click **"🎞️ Nối video"**
3. Xem log:
   ```
   ============================================================
   🎞️ GHÉP PHIM HOÀN CHỈNH
   ============================================================

   ✅ Scene 1: scene_001.mp4
   ✅ Scene 2: scene_002.mp4
   ✅ Scene 3: scene_003.mp4
   ✅ Scene 4: scene_004.mp4
   ✅ Scene 5: scene_005.mp4
   ✅ Scene 6: scene_006.mp4
   ✅ Scene 7: scene_007.mp4

   📊 Tổng số cảnh: 7/7

   ============================================================
   🔧 Bắt đầu ghép video...
   🎬 Đang nối 7 cảnh...
   ✅ Nối video hoàn tất!

   ============================================================
   🎉 PHIM HOÀN CHỈNH!
   ============================================================
   📝 Tên phim: Phở Việt Nam: Hương Vị Truyền Thống
   🎞️ Số cảnh: 7
   💾 Lưu tại: ./data/projects/20251025_123456/final.mp4
   ============================================================

   ✨ Phim của bạn đã sẵn sàng! Tải về và thưởng thức!
   ============================================================
   ```

4. Download file `final.mp4` từ video player

---

## 📁 Cấu trúc file output

```
./data/projects/20251025_123456/
├── videos/
│   ├── scene_001.mp4  (8s, 1080p)
│   ├── scene_002.mp4  (8s, 1080p)
│   ├── scene_003.mp4  (8s, 1080p)
│   ├── scene_004.mp4  (8s, 1080p)
│   ├── scene_005.mp4  (8s, 1080p)
│   ├── scene_006.mp4  (8s, 1080p)
│   └── scene_007.mp4  (8s, 1080p)
└── final.mp4          (56s, 1080p) ← Phim hoàn chỉnh
```

---

## ⚠️ Troubleshooting

### Lỗi: "Không thể tạo project"
**Nguyên nhân**: Flow API thay đổi hoặc cookies hết hạn

**Giải pháp**:
1. ✅ **Dùng Project ID có sẵn** (Option A)
2. Kiểm tra cookies còn hạn không
3. Update cookies mới từ browser

### Lỗi: "Không thể vào project"
**Nguyên nhân**: Project ID sai hoặc không có quyền

**Giải pháp**:
1. Kiểm tra lại Project ID (copy từ URL)
2. Đảm bảo đã đăng nhập đúng tài khoản
3. Thử tạo project mới trên Flow UI rồi lấy ID

### Lỗi: "Tất cả cảnh đều thất bại"
**Nguyên nhân**: Cookies hết hạn hoặc chưa vào project

**Giải pháp**:
1. Update cookies mới
2. Nhập Project ID vào field
3. Kiểm tra browser tự động có mở không

### Scene bị lỗi riêng lẻ
**Giải pháp**: Dùng tab "Xem & tạo lại" để regenerate scene đó

---

## 💡 Tips

### 1. **Luôn dùng Project ID có sẵn**
- Ổn định hơn
- Không bị lỗi tạo project
- Dễ quản lý

### 2. **Kiểm tra cookies thường xuyên**
```bash
# Test cookies còn hạn không
python manual_login_test.py
```

### 3. **Xem browser hoạt động**
- Tool chạy với `headless=False`
- Có thể xem browser đang làm gì
- Debug dễ dàng hơn

### 4. **Duration tối ưu**
- 0.5 - 1 phút: 4-7 scenes (nhanh)
- 1 - 2 phút: 7-15 scenes (trung bình)
- 2 - 3 phút: 15-22 scenes (lâu)

### 5. **Regenerate chiến lược**
- Không cần tất cả scenes phải hoàn hảo
- Chỉ regenerate scenes quan trọng
- Tiết kiệm thời gian

---

## 🎯 Example: Tạo phim 1 phút

```
1. Nhập:
   - Chủ đề: "Hướng dẫn pha cà phê Việt Nam"
   - Duration: 1 phút
   - Cookies: ./cookie.txt
   - Project ID: abc123def456

2. Click "Tạo kịch bản"
   → Gemini tạo 7 scenes

3. Click "Tạo tất cả video"
   → VEO tạo 7 videos × 8s = 56s
   → Mất khoảng 10-15 phút

4. Xem tab "Xem & tạo lại"
   → Scene 2 và 5 không đẹp
   → Click "Tạo lại" cho 2 scenes đó

5. Xem tab "Video cuối"
   → Click "Nối video"
   → Download final.mp4 (56s)

Done! 🎉
```

---

## 📞 Support

Nếu gặp lỗi:
1. Đọc phần Troubleshooting trên
2. Kiểm tra terminal logs
3. Xem browser tự động đang làm gì
4. Đảm bảo đã nhập Project ID

**Quan trọng nhất**: LUÔN dùng Project ID có sẵn! 🔑
