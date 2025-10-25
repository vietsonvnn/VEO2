# 🔑 KEY POINTS - VEO 3.1 Movie Production

## ⚡ Điểm quan trọng nhất

### 1. VEO 3.1 = 8 giây FIXED
```python
# ❌ SAI - VEO không có parameter duration
url = await controller.create_video_from_prompt(
    prompt="...",
    duration=8  # ❌ Lỗi: unexpected keyword argument
)

# ✅ ĐÚNG
url = await controller.create_video_from_prompt(
    prompt="..."  # VEO tự động tạo 8s
)
```

### 2. Workflow = Chia scenes
```
Phim 1 phút (60s)
  ↓
Chia thành 7 scenes × 8s
  ↓
VEO tạo 7 videos riêng biệt
  ↓
Ghép lại thành phim 56s
```

### 3. Prompt cho MỖI scene
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "veo_prompt": "Detailed prompt for scene 1...",
      "duration": 8  // Chỉ để biết, không truyền vào VEO
    },
    {
      "scene_number": 2,
      "veo_prompt": "Detailed prompt for scene 2...",
      "duration": 8
    }
  ]
}
```

---

## 📋 3 Tabs chính

### Tab 1️⃣: Tạo video
- **Input**: Topic + Duration (phút)
- **Output**: Script JSON + Tất cả videos

### Tab 2️⃣: Xem & tạo lại
- **Preview**: 10 scene slots với video player
- **Regenerate**: Click button để tạo lại scene

### Tab 3️⃣: Video cuối
- **Assemble**: Ghép tất cả scenes
- **Download**: file final.mp4

---

## 🎯 User Journey

```
1. Nhập topic: "Nấu phở"
2. Chọn duration: 1 phút
3. Click "Tạo kịch bản"
   → Gemini tạo 7 scenes
4. Click "Tạo tất cả video"
   → VEO tạo 7 videos × 8s
   → Log hiển thị tiến trình đẹp
5. Chuyển tab "Xem & tạo lại"
   → Xem từng video
   → Scene nào chưa đẹp → Click "Tạo lại"
6. Chuyển tab "Video cuối"
   → Click "Nối video"
   → Download final.mp4
```

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| **Script Gen** | Gemini 2.0 Flash |
| **Video Gen** | VEO 3.1 (8s fixed) |
| **Browser** | Playwright |
| **UI** | Gradio 5.49.1 |
| **Assembly** | MoviePy |
| **Language** | Python 3.12 |

---

## ⚠️ Lỗi đã fix

### ❌ Lỗi 1: Cookie sameSite
```python
# Fix trong flow_controller.py
for cookie in cookies:
    if 'sameSite' not in cookie or cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
        cookie['sameSite'] = 'Lax'  # Default
```

### ❌ Lỗi 2: Duration parameter
```python
# TRƯỚC (SAI):
url = await controller.create_video_from_prompt(
    prompt=scene['prompt'],
    duration=scene['duration']  # ❌ VEO không có parameter này
)

# SAU (ĐÚNG):
url = await controller.create_video_from_prompt(
    prompt=scene['prompt']  # ✅ VEO tự động 8s
)
```

### ❌ Lỗi 3: Duration input
```python
# TRƯỚC: Slider tính bằng giây (20-90s)
duration = gr.Slider(20, 90, 30, step=10, label="⏱️ Thời lượng (s)")

# SAU: Slider tính bằng phút (0.5-3 phút)
duration = gr.Slider(0.5, 3, 1, step=0.5, label="⏱️ Thời lượng (phút)")

# Convert trong code:
duration_seconds = int(duration_minutes * 60)
```

---

## 📊 Progress Logs

### Format đẹp với emoji & box:
```
============================================================
🎬 BẮT ĐẦU SẢN XUẤT PHIM
============================================================
📝 Kịch bản: [Tên]
🎞️ Tổng số cảnh: X
⏱️ Thời lượng: Xs
============================================================

────────────────────────────────────────────────────────────
🎬 SCENE 1/7
📝 Mô tả: ...

   ⏳ Đang tạo video (VEO 3.1)...
   ✅ Video đã tạo xong!
   📥 Đang download (1080p)...
   ✅ Download hoàn tất!
   💾 Lưu tại: scene_001.mp4
   ✨ Scene 1: HOÀN THÀNH

============================================================
📊 KẾT QUẢ CUỐI CÙNG
============================================================
✅ Hoàn thành: 7/7 cảnh
============================================================
🎉 HOÀN THÀNH TOÀN BỘ!
============================================================
```

---

## ✅ Checklist triển khai

- [x] Fix cookie sameSite
- [x] Duration input = phút (không phải giây)
- [x] Xóa duration parameter khỏi create_video_from_prompt()
- [x] Progress logs đẹp với emoji & borders
- [x] Script generator chia scenes = total_duration / 8
- [x] Preview tab với 10 scene slots
- [x] Regenerate button cho mỗi scene
- [x] Final assembly với MoviePy
- [x] Beautiful UI với Glass theme

---

## 🚀 Ready to use

**URL**: http://localhost:7860

**Status**: ✅ All systems operational

**Cookie**: `./cookie.txt` (đã fix sameSite)

**API Key**: Đã set trong `.env`
