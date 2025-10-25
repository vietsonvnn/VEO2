# 🎬 VEO 3.1 Movie Production Workflow

## 📋 Tổng quan

Tool này được thiết kế để sản xuất **phim dài** từ VEO 3.1 bằng cách chia thành nhiều **scenes 8 giây** và ghép lại.

## ⚙️ Tại sao phải chia thành scenes?

### Giới hạn của VEO 3.1:
- ✅ VEO 3.1 chỉ tạo được video **tối đa 8 giây**
- ❌ Không thể tạo video dài hơn 8 giây trong 1 lần

### Giải pháp:
1. **Chia kịch bản** thành nhiều scenes 8s
2. **Tạo từng scene** riêng biệt (mỗi scene = 1 video 8s)
3. **Ghép tất cả scenes** lại thành phim hoàn chỉnh

---

## 🔄 Workflow chi tiết

### **BƯỚC 1: Tạo kịch bản** (Tab 1)

#### Input:
- **Topic**: Chủ đề phim (VD: "Hướng dẫn nấu phở")
- **Duration**: Thời lượng phim (VD: 1 phút = 60s)

#### Process:
```
ScriptGenerator (Gemini 2.0 Flash)
  ↓
Tính số scenes = Duration / 8
  ↓ (60s / 8s = 7-8 scenes)
Tạo prompt VEO cho từng scene
```

#### Output: Kịch bản JSON
```json
{
  "title": "Hướng Dẫn Nấu Phở",
  "total_duration": 60,
  "num_scenes": 7,
  "scenes": [
    {
      "scene_number": 1,
      "duration": 8,
      "description": "Cảnh quay nguyên liệu tươi",
      "veo_prompt": "Close-up shot of fresh ingredients: rice noodles, beef slices, herbs..."
    },
    {
      "scene_number": 2,
      "duration": 8,
      "description": "Ninh xương bò",
      "veo_prompt": "Steam rising from a large pot of simmering beef bones..."
    }
    // ... 5 scenes nữa
  ]
}
```

**Mỗi scene có:**
- `description`: Mô tả cảnh (Vietnamese)
- `veo_prompt`: Prompt chi tiết cho VEO 3.1 (English, 100-200 words)
- `duration`: 8 giây (fixed)
- `camera_movement`: Kiểu chuyển động camera
- `mood`, `lighting`: Phong cách

---

### **BƯỚC 2: Tạo tất cả video** (Tab 1)

#### Process:
```
For each scene in scenes:
  1. Gọi VEO 3.1 API
     ↓
     create_video_from_prompt(prompt=scene.veo_prompt)
     ↓
  2. Chờ VEO tạo video (8s)
     ↓
  3. Download video 1080p
     ↓
     Lưu: scene_001.mp4, scene_002.mp4, ...
```

#### Output:
```
./data/projects/20251025_123456/videos/
  ├── scene_001.mp4  (8s)
  ├── scene_002.mp4  (8s)
  ├── scene_003.mp4  (8s)
  ├── scene_004.mp4  (8s)
  ├── scene_005.mp4  (8s)
  ├── scene_006.mp4  (8s)
  └── scene_007.mp4  (8s)
```

**Log hiển thị:**
```
============================================================
🎬 BẮT ĐẦU SẢN XUẤT PHIM
============================================================
📝 Kịch bản: Hướng Dẫn Nấu Phở
🎞️ Tổng số cảnh: 7
⏱️ Thời lượng: 60s
============================================================

────────────────────────────────────────────────────────────
🎬 SCENE 1/7
📝 Mô tả: Cảnh quay nguyên liệu tươi...

   ⏳ Đang tạo video (VEO 3.1)...
   ✅ Video đã tạo xong!
   📥 Đang download (1080p)...
   ✅ Download hoàn tất!
   💾 Lưu tại: scene_001.mp4
   ✨ Scene 1: HOÀN THÀNH

[Lặp lại cho 6 scenes còn lại...]

============================================================
📊 KẾT QUẢ CUỐI CÙNG
============================================================
✅ Hoàn thành: 7/7 cảnh
============================================================
🎉 HOÀN THÀNH TOÀN BỘ!
============================================================
```

---

### **BƯỚC 3: Xem & Tạo lại** (Tab 2)

#### Mục đích:
- User **preview từng scene**
- **Tạo lại** scene nào chưa ưng ý

#### UI:
```
┌─────────────────────────────────┐
│ Scene 1                         │
├─────────────────────────────────┤
│ [Video Player]  │ [Tạo lại]     │
│ scene_001.mp4   │               │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Scene 2                         │
├─────────────────────────────────┤
│ [Video Player]  │ [Tạo lại]     │
│ scene_002.mp4   │               │
└─────────────────────────────────┘

... (10 scene slots)
```

#### Regenerate workflow:
```
User clicks "Tạo lại Scene 3"
  ↓
VEO 3.1 tạo lại video với CÙNG prompt
  ↓
Download & thay thế scene_003.mp4
  ↓
Video player tự động update
```

**Tại sao cần regenerate?**
- VEO 3.1 là AI generative → mỗi lần chạy khác nhau
- Scene có thể không đẹp hoặc không match ý user
- User có quyền tạo lại nhiều lần đến khi hài lòng

---

### **BƯỚC 4: Ghép phim cuối** (Tab 3)

#### Process:
```python
VideoAssembler (MoviePy)
  ↓
Load all completed scenes:
  - scene_001.mp4 (8s)
  - scene_002.mp4 (8s)
  - ...
  - scene_007.mp4 (8s)
  ↓
Concatenate (nối video):
  clip1 → clip2 → clip3 → ... → clip7
  ↓
Export final.mp4 (56s)
```

#### Output:
```
./data/projects/20251025_123456/final.mp4
```

**Final video:**
- Duration: 56s (7 scenes × 8s)
- Quality: 1080p
- Format: MP4 (H.264 + AAC)
- Seamless transitions

---

## 🎯 Ví dụ thực tế

### Input:
- Topic: "Hướng dẫn nấu phở Việt Nam"
- Duration: 1 phút (60s)

### Script Generation:
```
60s / 8s = 7.5 → Làm tròn thành 7 scenes
```

### 7 Scenes:
1. **Scene 1** (8s): Cảnh nguyên liệu tươi
2. **Scene 2** (8s): Ninh xương bò
3. **Scene 3** (8s): Phi thơm hành gừng
4. **Scene 4** (8s): Nêm nếm gia vị
5. **Scene 5** (8s): Trình bày phở ra tô
6. **Scene 6** (8s): Chan nước dùng
7. **Scene 7** (8s): Cận cảnh tô phở hoàn chỉnh

### Video Generation:
```
VEO 3.1 tạo 7 videos:
  scene_001.mp4 ✅ (8s)
  scene_002.mp4 ✅ (8s)
  scene_003.mp4 ❌ (không đẹp)
  scene_004.mp4 ✅ (8s)
  scene_005.mp4 ✅ (8s)
  scene_006.mp4 ✅ (8s)
  scene_007.mp4 ✅ (8s)
```

### User action:
```
Xem scene 3 → Chưa đẹp → Click "Tạo lại"
  ↓
VEO tạo lại scene_003.mp4
  ↓
scene_003.mp4 ✅ (OK rồi)
```

### Final Assembly:
```
Nối 7 scenes → final.mp4 (56s)
```

---

## 💡 Ưu điểm của workflow này

### 1. **Vượt qua giới hạn 8s**
- VEO chỉ làm được 8s → Tool tạo phim dài vô hạn

### 2. **Kiểm soát chất lượng**
- Preview từng scene
- Tạo lại scene không ưng

### 3. **Tiết kiệm thời gian**
- Không cần tạo lại toàn bộ phim
- Chỉ regenerate scene cần thiết

### 4. **Tự động hoàn toàn**
- Từ topic → kịch bản → videos → final
- User chỉ cần input topic + duration

### 5. **Linh hoạt**
- Có thể tạo phim bất kỳ độ dài
- 0.5 phút, 1 phút, 2 phút, 3 phút...

---

## 🔧 Technical Details

### Scene Duration = 8s (Fixed)
```python
# VEO 3.1 API
def create_video_from_prompt(
    prompt: str,
    aspect_ratio: str = "16:9"
    # ❌ KHÔNG có parameter duration
) -> str:
    # VEO tự động tạo 8s
    # Không thể thay đổi
```

### Script Generation Formula
```python
num_scenes = total_duration // 8

# Example:
# 60s / 8 = 7.5 → 7 scenes
# 90s / 8 = 11.25 → 11 scenes
# 120s / 8 = 15 scenes
```

### Video Assembly
```python
from moviepy.editor import VideoFileClip, concatenate_videoclips

clips = [VideoFileClip(f) for f in video_files]
final = concatenate_videoclips(clips, method="compose")
final.write_videofile("final.mp4", codec='libx264')
```

---

## 📊 Luồng dữ liệu

```
User Input
  ↓
┌─────────────────────────┐
│ Topic: "Nấu phở"        │
│ Duration: 1 phút (60s)  │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ ScriptGenerator         │
│ (Gemini 2.0 Flash)      │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ Script JSON             │
│ - 7 scenes              │
│ - VEO prompts           │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ FlowController          │
│ (Browser Automation)    │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ VEO 3.1 API             │
│ - Generate 7 videos     │
│ - Each 8s               │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ 7 MP4 files             │
│ scene_001.mp4 - 007.mp4 │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ User Preview            │
│ - Watch each scene      │
│ - Regenerate if needed  │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ VideoAssembler          │
│ (MoviePy)               │
└─────────────────────────┘
  ↓
┌─────────────────────────┐
│ final.mp4 (56s)         │
│ Complete Movie          │
└─────────────────────────┘
```

---

## ✅ Kết luận

**Đây là workflow sản xuất phim chuyên nghiệp:**

1. ✅ **Tự động**: AI tạo kịch bản + video
2. ✅ **Linh hoạt**: Bất kỳ độ dài nào
3. ✅ **Kiểm soát**: Preview & regenerate
4. ✅ **Chất lượng**: 1080p, smooth transitions
5. ✅ **Đơn giản**: User chỉ cần input topic

**Tool này biến VEO 3.1 từ "8s video generator" thành "Complete Movie Production Studio"! 🎬**
