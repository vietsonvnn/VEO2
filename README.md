# 🎬 VEO 3.1 - Movie Production System

> **Sản xuất phim tự động - Từ ý tưởng đến phim hoàn chỉnh**

## ✅ Status: READY TO USE

**URL**: http://localhost:7860  
**API Key**: ✅ Configured  
**Theme**: Modern Glass  
**Mode**: Full Auto Production

---

## 🎯 Concept

**Bạn là đạo diễn, tool là ekip sản xuất**

1. **Bạn**: Đưa ý tưởng phim (chủ đề + thời lượng)
2. **AI**: Viết kịch bản + chia cảnh
3. **Tool**: Quay tất cả cảnh tự động
4. **Bạn**: Xem & chỉnh sửa (tạo lại cảnh không ưng)
5. **Tool**: Ghép phim hoàn chỉnh

**= 1 file .mp4 sẵn sàng upload**

---

## 🚀 Quick Start

```bash
# UI đang chạy sẵn, chỉ cần mở browser:
open http://localhost:7860

# Hoặc khởi động lại:
source venv312/bin/activate && python app.py
```

---

## 📋 Workflow 3 Bước

### 1️⃣ Tạo & Quay (Tab 1)

**Input**:
- Chủ đề: "Phim tài liệu về phở Việt Nam"
- Thời lượng: 60s

**Click**: "Tạo kịch bản" → "Tạo tất cả video"

**Output**:
- 7-8 cảnh đã quay (1080p)
- Thời gian: 10-15 phút

---

### 2️⃣ Xem & Sửa (Tab 2)

**Mục đích**: Quality control

```
Foreach scene:
  Play video
  If (OK):
    → Next scene
  Else:
    → Click "Tạo lại Scene X"
    → Wait 2-3 phút
    → Review lại
```

**Kết quả**: Tất cả cảnh đều ưng ý

---

### 3️⃣ Ghép Phim (Tab 3)

**Click**: "Nối video"

**Output**: 
- File `.mp4` hoàn chỉnh
- Tất cả cảnh đã ghép mượt
- Ready to upload

---

## 💡 Tính năng

✅ **100% Tự động**:
- Viết kịch bản: AI
- Quay cảnh: VEO 3.1
- Download: 1080p auto
- Ghép phim: MoviePy

✅ **Quality Control**:
- Preview từng cảnh
- Tạo lại không giới hạn
- Chỉ giữ cảnh đẹp

✅ **Professional**:
- Theme đẹp
- Progress tracking
- State management
- Error handling

---

## 📊 Example

**Phim "Văn hóa Phở" (60s)**:

```
1. Input:
   - Chủ đề: "Tài liệu về phở Việt Nam"
   - 60s

2. AI tạo 7 cảnh:
   Scene 1: Nước dùng sôi (8s)
   Scene 2: Xắt thịt (8s)
   Scene 3: Luộc bánh phở (8s)
   Scene 4: Gia vị (8s)
   Scene 5: Bày tô (8s)
   Scene 6: Múc nước dùng (8s)
   Scene 7: Thành phẩm (8s)

3. Tool quay 7 videos (10 phút)

4. Review:
   Scene 1-3: ✅ OK
   Scene 4: ❌ Không đẹp → Tạo lại ✅
   Scene 5-7: ✅ OK

5. Ghép → final.mp4 (60s)

Total: ~15 phút
```

---

## 🎨 UI Tabs

### Tab 1: Tạo video
- Input chủ đề + thời lượng
- Tạo kịch bản
- Quay tất cả cảnh

### Tab 2: Xem & tạo lại
- Preview từng cảnh
- Play video
- Regenerate button

### Tab 3: Video cuối
- Ghép phim hoàn chỉnh
- Download final video

---

## 📁 Files

**Launcher**: `python app.py` (đang chạy)  
**API Key**: `.env`  
**Cookies**: `./cookie.txt`  
**Output**: `./data/projects/*/final.mp4`

**Docs**:
- [FINAL.md](FINAL.md) - Production guide chi tiết
- [START_HERE.md](START_HERE.md) - Quick start

---

## ⚙️ Tech Stack

- **UI**: Gradio 5.49.1 (Glass theme)
- **AI Script**: Gemini 2.0 Flash
- **Video Gen**: VEO 3.1
- **Automation**: Playwright
- **Assembly**: MoviePy
- **Python**: 3.12.12

---

## 🎯 Use Cases

1. **YouTube Creator**: Phim 60s cho shorts
2. **TikTok/Reels**: Phim 30s viral
3. **Documentary**: Phim dài 90s
4. **Product Review**: Demo sản phẩm
5. **Tutorial**: Hướng dẫn step-by-step

---

## ✨ Highlights

- **Tự động 100%**: Chỉ cần ý tưởng
- **Quality First**: Tạo lại đến khi OK
- **Production Ready**: Professional workflow
- **Modern UI**: Đẹp & dễ dùng
- **Fast**: 10-20 phút → phim hoàn chỉnh

---

**Ready to create your movie! 🎬**

```
http://localhost:7860
```
