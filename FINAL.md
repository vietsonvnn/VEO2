# 🎬 VEO 3.1 - Movie Production Tool

## ✅ Đang chạy: http://localhost:7860

---

## 🎯 Mục đích: Tạo "BỘ PHIM" hoàn chỉnh

Bạn là **đạo diễn phim**, tool này giúp bạn:

1. **Viết kịch bản phim** (AI tự động)
2. **Quay từng cảnh** (VEO 3.1 AI)
3. **Xem lại & chỉnh sửa** (Preview + Regenerate)
4. **Ghép phim hoàn chỉnh** (Assembly)
5. **Xuất file phim** (Download)

---

## 🎬 Workflow - Làm Phim 3 Bước

### BƯỚC 1: Tạo Kịch Bản & Quay Phim

**Tab "Tạo video"**:

1. **Nhập chủ đề phim**:
   - VD: "Phim tài liệu về văn hóa phở Việt Nam"
   - VD: "Review chi tiết iPhone 16 Pro Max"
   - VD: "Hành trình khám phá Đà Nẵng"

2. **Chọn thời lượng phim**:
   - Phim ngắn: 20-30s (2-4 cảnh)
   - Phim trung: 30-60s (4-8 cảnh)
   - Phim dài: 60-90s (8-12 cảnh)

3. Click **"Tạo kịch bản"**
   - AI tự động viết kịch bản
   - Chia thành các cảnh (mỗi cảnh 8s)

4. Click **"Tạo tất cả video"**
   - Tool tự động quay từng cảnh
   - Download về 1080p
   - Hiển thị progress

---

### BƯỚC 2: Xem Phim & Chỉnh Sửa

**Tab "Xem & tạo lại"**:

**Mục đích**: 
- Xem lại từng cảnh đã quay
- Quyết định cảnh nào giữ, cảnh nào bỏ
- Quay lại cảnh không ưng ý

**Cách dùng**:

```
Scene 1: [Video Player]
  ├─ ✅ Cảnh đẹp → Giữ lại
  └─ Mô tả: "Nồi phở đang sôi..."

Scene 2: [Video Player]  
  ├─ ❌ Không ưng → Click "Tạo lại Scene 2"
  └─ Tool sẽ quay lại cảnh này với cùng kịch bản

Scene 3: [Video Player]
  ├─ ✅ OK → Giữ lại
  └─ ...
```

**Chu trình**:
1. Play video từng cảnh
2. Nếu OK → Bỏ qua, sang cảnh tiếp
3. Nếu chưa OK → Click "Tạo lại Scene X"
4. Xem lại cảnh mới → Repeat until OK

---

### BƯỚC 3: Ghép Phim Hoàn Chỉnh

**Tab "Video cuối"**:

1. Click **"Nối video"**
2. Tool tự động:
   - Lấy TẤT CẢ cảnh đã OK
   - Ghép theo thứ tự (Scene 1 → 2 → 3...)
   - Export file `.mp4`

3. **Kết quả**:
   - 1 file phim hoàn chỉnh
   - Tất cả cảnh đã nối mượt
   - Sẵn sàng upload YouTube/TikTok

---

## 📊 Ví dụ Thực Tế

### Phim "Văn hóa Phở Việt Nam" (60s)

**Kịch bản AI tạo** (60s / 8s = ~7 cảnh):

```
Scene 1: Nồi nước dùng đang sôi (8s)
Scene 2: Xắt thịt bò mỏng (8s)  
Scene 3: Luộc bánh phở (8s)
Scene 4: Chuẩn bị gia vị (8s)
Scene 5: Bày biện tô phở (8s)
Scene 6: Múc nước dùng vào tô (8s)
Scene 7: Thành phẩm tô phở hoàn chỉnh (8s)
```

**Quá trình**:

1. **Tạo & Quay** (Tab 1):
   - AI tạo 7 cảnh
   - Tool quay 7 videos (5-10 phút)

2. **Preview & Edit** (Tab 2):
   ```
   Scene 1: ✅ Đẹp
   Scene 2: ❌ Không rõ → Tạo lại → ✅ OK
   Scene 3: ✅ Đẹp
   Scene 4: ✅ Đẹp
   Scene 5: ❌ Góc quay xấu → Tạo lại → ✅ OK
   Scene 6: ✅ Đẹp
   Scene 7: ✅ Đẹp
   ```

3. **Ghép phim** (Tab 3):
   - 7 cảnh → 1 phim 60s
   - File: `van_hoa_pho_final.mp4`

**Timeline**:
- Tạo kịch bản: 30s
- Quay 7 cảnh: 7-10 phút
- Tạo lại 2 cảnh: 3-4 phút  
- Ghép phim: 30s
- **Total**: ~15 phút

---

## 🎯 Use Cases

### 1. YouTube Content Creator
```
Chủ đề: "Top 5 món ăn đường phố Hà Nội"
Thời lượng: 60s
Cảnh: 7-8 cảnh (mỗi món 1 cảnh + intro/outro)

Workflow:
  → Tạo kịch bản
  → Quay 8 cảnh
  → Preview: Giữ 6, tạo lại 2
  → Ghép phim → Upload YouTube
```

### 2. TikTok/Reels Creator
```
Chủ đề: "Quy trình làm cà phê"
Thời lượng: 30s
Cảnh: 3-4 cảnh nhanh

Workflow:
  → Tạo kịch bản ngắn
  → Quay 4 cảnh
  → Preview: Tất cả OK
  → Ghép → Post TikTok
```

### 3. Documentary Maker
```
Chủ đề: "Hành trình khám phá Phú Quốc"
Thời lượng: 90s
Cảnh: 10-12 cảnh

Workflow:
  → Tạo kịch bản chi tiết
  → Quay 12 cảnh (locations khác nhau)
  → Preview: Kiểm tra từng cảnh kỹ
  → Tạo lại 3-4 cảnh không đẹp
  → Ghép phim dài → Upload
```

---

## ⚙️ Quy trình Chi Tiết

### Phase 1: Pre-Production

**Input từ user**:
- Chủ đề phim
- Thời lượng mong muốn

**AI xử lý**:
- Phân tích chủ đề
- Tạo outline kịch bản
- Chia thành N cảnh (duration / 8s)
- Viết mô tả từng cảnh
- Tối ưu prompt cho VEO

**Output**:
- File `script.json` với kịch bản hoàn chỉnh
- Danh sách scenes

### Phase 2: Production

**Tool tự động**:
- Mở Google Labs Flow
- Tạo video từng scene:
  - Nhập prompt
  - Set duration (8s)
  - Chờ VEO generate
  - Download (1080p với upscale)
- Lưu videos vào project folder

**Progress tracking**:
- Scene 1/7: Creating...
- Scene 2/7: Downloading...
- Scene 3/7: Completed ✅
- ...

### Phase 3: Post-Production

**User review**:
- Xem từng cảnh
- Đánh giá chất lượng
- Quyết định:
  - ✅ Keep → Giữ lại
  - ❌ Regenerate → Quay lại

**Edit loop**:
```
while (có cảnh chưa OK):
    Preview scene
    if (không ưng):
        Click "Tạo lại"
        Wait for new video
        Preview again
    else:
        Mark as approved
```

### Phase 4: Final Assembly

**Tool ghép phim**:
- Collect all approved scenes
- Sort theo thứ tự (1 → 2 → 3...)
- Concat videos:
  - Resize về cùng resolution
  - Giữ audio
  - Smooth transitions
- Export final `.mp4`

**Output**:
- File phim hoàn chỉnh
- Ready to upload

---

## 📁 Project Structure

```
./data/projects/20241025_140000/
├── script.json              # Kịch bản phim
├── videos/                  # Scenes videos
│   ├── scene_001.mp4       # Cảnh 1
│   ├── scene_002.mp4       # Cảnh 2 (regenerated)
│   ├── scene_003.mp4       # Cảnh 3
│   └── ...
└── final.mp4                # 🎬 PHIM HOÀN CHỈNH
```

---

## 💡 Tips & Best Practices

### Viết chủ đề tốt

✅ **TỐT**:
- "Phim tài liệu về quy trình làm phở truyền thống"
- "Hành trình khám phá 5 bãi biển đẹp nhất Việt Nam"
- "Review chi tiết MacBook Pro M3 - Performance, Design, Battery"

❌ **KHÔNG TỐT**:
- "Video về ẩm thực" (quá chung)
- "Review đồ điện tử" (không cụ thể)

### Chọn thời lượng hợp lý

| Platform | Duration | Scenes | Note |
|----------|----------|--------|------|
| TikTok | 15-30s | 2-4 | Nhanh, catchy |
| Reels | 20-40s | 3-5 | Dynamic |
| YouTube Shorts | 30-60s | 4-8 | Standard |
| YouTube Video | 60-90s | 8-12 | Chi tiết |

### Preview kỹ lưỡng

**Checklist khi xem cảnh**:
- [ ] Hình ảnh rõ nét?
- [ ] Nội dung đúng kịch bản?
- [ ] Góc quay đẹp?
- [ ] Lighting tốt?
- [ ] Chuyển động mượt?

Nếu 1 trong các điểm trên không OK → **Tạo lại cảnh**

### Tạo lại thông minh

**Khi nào nên tạo lại**:
- Hình ảnh mờ/tối
- Nội dung sai lệch
- Góc quay xấu
- Chuyển động giật
- Không match với cảnh trước/sau

**Lưu ý**:
- Có thể tạo lại nhiều lần
- Mỗi lần ~2-3 phút
- Tool giữ nguyên prompt, chỉ generate lại

---

## 🎬 Status hiện tại

```
✅ UI đang chạy: http://localhost:7860
✅ API Key: Configured  
✅ Theme: Modern Glass (đẹp)
✅ Cookies: ./cookie.txt

🎯 Features:
  ✅ Tạo kịch bản tự động
  ✅ Quay từng cảnh (1080p)
  ✅ Preview videos
  ✅ Regenerate scenes
  ✅ Ghép phim hoàn chỉnh
```

---

## 🚀 Bắt đầu ngay

Mở browser: **http://localhost:7860**

Làm theo 3 bước:
1. Tab 1: Tạo kịch bản + Quay phim
2. Tab 2: Xem & sửa từng cảnh
3. Tab 3: Ghép phim cuối

**Đơn giản - Trực quan - Chuyên nghiệp!** 🎬✨
