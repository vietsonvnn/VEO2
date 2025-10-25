# VEO 3.1 Complete Automation System - User Guide

## 📋 Tổng quan

Hệ thống tự động hóa hoàn chỉnh cho việc tạo video bằng VEO 3.1 AI, từ khởi tạo dự án đến video hoàn thiện sẵn sàng upload lên YouTube.

## 🎯 Quy trình hoàn chỉnh (12 bước)

### 1️⃣ **Khởi tạo dự án**

**Mục đích**: Thiết lập dự án mới với các cấu hình cơ bản

**Các bước**:

1. **Tải API Key**:
   - Chuẩn bị file `.txt` chứa Gemini API key
   - Upload file trong giao diện
   - Hệ thống tự động kiểm tra và lưu vào `.env`

2. **Thiết lập dự án**:
   - **Tên dự án**: VD: `video_marketing_2024`
   - **Thư mục lưu**: Mặc định `./data/projects`
   - **Chọn mô hình AI**:
     - `gemini-2.0-flash-exp` (khuyên dùng - nhanh và mới nhất)
     - `gemini-1.5-pro` (chất lượng cao hơn)
     - `gemini-1.5-flash` (nhanh và rẻ)

3. Nhấn **"Khởi tạo dự án"**

**Kết quả**:
- Tạo thư mục dự án: `./data/projects/{project_id}_{project_name}/`
- Tạo các thư mục con: `scenes/`, `downloads/`, `characters/`
- Lưu file `project_state.json` để tracking

---

### 2️⃣ **Tạo kịch bản**

**Mục đích**: AI tự động tạo kịch bản video dựa trên chủ đề

**Các bước**:

1. **Nhập thông tin cơ bản**:
   - **Chủ đề**: VD: "Hướng dẫn làm bánh pizza tại nhà"
   - **Tổng thời lượng**: 60 giây (10-300s)
   - **Thời lượng mỗi cảnh**: 8 giây (3-20s)
   - **Phong cách**: Realistic / Cinematic / Artistic / Documentary / Animated
   - **Tỷ lệ**: 16:9 (YouTube) / 9:16 (TikTok, Reels) / 1:1 (Instagram)

2. **Cấu hình nhân vật** (tùy chọn):
   - **Không có nhân vật**: Video không có người
   - **AI tự nhận diện**: AI tự tạo và duy trì nhân vật nhất quán
   - **Upload ảnh nhân vật**: Upload 1-3 ảnh nhân vật + mô tả chi tiết

3. Nhấn **"Tạo kịch bản"**

**Kết quả**:
- File `script.json` chứa toàn bộ kịch bản
- Chia tự động thành các scenes dựa trên thời lượng
- Mỗi scene có:
  - `description`: Mô tả cảnh
  - `veo_prompt`: Prompt tối ưu cho VEO 3.1
  - `duration`: Thời lượng
  - `camera_movement`: Chuyển động camera

**Ví dụ kịch bản**:
```json
{
  "title": "Hướng dẫn làm bánh pizza tại nhà",
  "description": "Video hướng dẫn...",
  "style": "Cinematic",
  "aspect_ratio": "16:9",
  "scenes": [
    {
      "scene_number": 1,
      "description": "Các nguyên liệu trên bàn bếp",
      "veo_prompt": "A cinematic shot of fresh pizza ingredients...",
      "duration": 8,
      "camera_movement": "slow zoom in"
    },
    ...
  ]
}
```

---

### 3️⃣ **Tạo nội dung SEO**

**Mục đích**: Tự động tạo tiêu đề, mô tả, tags, thumbnail prompt cho YouTube

**Các bước**:

1. Nhấn **"Tạo nội dung SEO"**
2. Hệ thống tự động phân tích kịch bản và tạo:
   - **Tiêu đề**: Tối ưu cho YouTube SEO
   - **Mô tả**: Chi tiết với timestamps
   - **Tags**: 15 tags phù hợp
   - **Thumbnail Prompt**: Prompt để tạo thumbnail bằng AI

**Kết quả**:
- File `seo_content.txt` sẵn sàng copy-paste lên YouTube

**Ví dụ SEO content**:
```
TIÊU ĐỀ:
🍕 Cách làm bánh Pizza tại nhà - Công thức đơn giản cho người mới

MÔ TẢ:
🎬 Cách làm bánh Pizza tại nhà - Công thức đơn giản cho người mới

📝 Mô tả:
Hướng dẫn chi tiết cách làm bánh pizza...

🎯 Các cảnh trong video:
1. Các nguyên liệu trên bàn bếp
2. Nhào bột pizza
...

TAGS:
pizza, làm bánh, cooking, ...

THUMBNAIL PROMPT:
Tạo thumbnail cho video: ... Style: Cinematic, bold text overlay...
```

---

### 4️⃣ **Sinh video cho từng phân cảnh**

**Mục đích**: Tự động tạo video cho tất cả scenes bằng VEO 3.1

**Các bước**:

1. **Cấu hình**:
   - **File cookies**: `./config/cookies.json` (đã extract từ browser)
   - **Chạy ẩn (headless)**: Bật để chạy nền, tắt để xem quá trình

2. Nhấn **"Tạo tất cả video"**

**Quá trình**:
- Hệ thống tự động:
  1. Mở Google Labs Flow
  2. Đăng nhập bằng cookies
  3. Tạo video cho từng scene:
     - Nhập prompt
     - Chọn duration
     - Chọn aspect ratio
     - Chờ video được tạo
     - Lưu URL video
  4. Cập nhật trạng thái realtime

**Trạng thái scenes**:
- `⏳ pending`: Chưa tạo
- `🎬 generating`: Đang tạo
- `✅ completed`: Hoàn thành
- `❌ failed`: Thất bại
- `🚫 rejected`: Bị từ chối (cần tạo lại)

**Kết quả**:
```
✅ Scene 1: Hoàn thành
✅ Scene 2: Hoàn thành
❌ Scene 3: Thất bại - Timeout
✅ Scene 4: Hoàn thành
...
```

---

### 5️⃣ **Xem trước & phê duyệt**

**Mục đích**: Kiểm tra chất lượng video, từ chối video không ưng ý

**Các bước**:

1. **Xem tổng quan**:
   - Nhấn **"Làm mới danh sách"** để xem tất cả scenes
   - Kiểm tra status và approval status

2. **Xem chi tiết từng scene**:
   - Kéo slider để chọn scene
   - Xem video preview
   - Đọc prompt và status

3. **Phê duyệt hoặc từ chối**:
   - ✅ **Phê duyệt**: Video OK, sẽ được download và nối vào video cuối
   - ❌ **Từ chối**: Video không ưng, đánh dấu để tạo lại

4. **Tạo lại scene bị từ chối**:
   - Chọn scene bị từ chối
   - Nhấn **"Tạo lại scene này"**
   - Video mới sẽ được tạo với cùng prompt

**Ví dụ workflow**:
```
Scene 1: ✅ Approved
Scene 2: ✅ Approved
Scene 3: ❌ Rejected (không đúng phong cách) → Tạo lại
Scene 4: ✅ Approved
Scene 3 (new): ✅ Approved
```

---

### 6️⃣ **Tải video hàng loạt**

**Mục đích**: Download tất cả video đã approved với quality cao nhất

**Các bước**:

1. **Chọn chất lượng**:
   - **1080p** (khuyên dùng): Auto-upscale lên 1080p
   - **720p**: Quality gốc

2. Nhấn **"Tải tất cả video"**

**Quá trình Auto-Upscale**:
- Hệ thống tự động:
  1. Thử download 1080p:
     - Click menu "Tải xuống"
     - Chọn "Đã tăng độ phân giải (1080p)"
     - Chờ upscale (1-5 phút)
     - Download file
  2. Nếu 1080p thất bại → Fallback về 720p:
     - Click menu "Tải xuống"
     - Chọn "720p"
     - Download file

**Kết quả**:
```
✅ Scene 1: Downloaded 1080p
✅ Scene 2: Downloaded 1080p
⚠️ Scene 4: Downloaded 720p (1080p failed)
```

**Files được lưu**:
```
./data/projects/{project}/downloads/
  ├── scene_001_1080p.mp4
  ├── scene_002_1080p.mp4
  ├── scene_004_720p.mp4
  └── ...
```

---

### 7️⃣ **Nối video hoàn chỉnh**

**Mục đích**: Ghép tất cả scenes thành 1 video hoàn chỉnh

**Các bước**:

1. Nhấn **"Nối video"**

**Quá trình**:
- Hệ thống tự động:
  1. Lấy tất cả scenes đã approved (theo thứ tự)
  2. Sử dụng MoviePy để nối video:
     - Resize về cùng resolution nếu cần
     - Giữ nguyên audio
     - Thêm transition mượt (optional)
  3. Export video cuối

**Kết quả**:
- File: `./data/projects/{project}/{project_name}_final.mp4`
- Video hoàn chỉnh, sẵn sàng upload YouTube

---

## 🗂️ Cấu trúc thư mục dự án

```
./data/projects/20241025_143000_video_marketing/
├── project_state.json          # Trạng thái dự án
├── script.json                 # Kịch bản
├── seo_content.txt            # Nội dung SEO
├── video_marketing_final.mp4  # Video hoàn chỉnh
│
├── characters/                # Ảnh nhân vật (nếu có)
│   ├── character_1.jpg
│   └── character_2.jpg
│
├── scenes/                    # Metadata scenes
│   └── (reserved)
│
└── downloads/                 # Video scenes đã download
    ├── scene_001_1080p.mp4
    ├── scene_002_1080p.mp4
    ├── scene_003_720p.mp4
    └── ...
```

---

## 📊 Project State Management

File `project_state.json` lưu trữ toàn bộ trạng thái:

```json
{
  "project_id": "20241025_143000",
  "project_name": "video_marketing",
  "model": "gemini-2.0-flash-exp",
  "script": { ... },
  "scenes": [
    {
      "scene_index": 0,
      "scene_number": 1,
      "prompt": "A cinematic shot...",
      "description": "Các nguyên liệu...",
      "duration": 8,
      "status": "completed",
      "video_url": "https://labs.google/flow/...",
      "download_path": "./downloads/scene_001_1080p.mp4",
      "approved": true,
      "error": null
    },
    ...
  ],
  "seo_content": "...",
  "final_video_path": "./video_marketing_final.mp4",
  "last_updated": "2024-10-25T14:30:00"
}
```

---

## 🎬 Tính năng nâng cao

### Character Consistency

**AI tự nhận diện**:
- AI tự động tạo và duy trì nhân vật xuyên suốt video
- Prompt được tối ưu để đảm bảo consistency

**Upload ảnh nhân vật**:
- Upload 1-3 ảnh reference
- Mô tả chi tiết: "Một đầu bếp nam, 30 tuổi, mặc đồng phục trắng, râu nhẹ..."
- AI sẽ tham khảo để tạo nhân vật giống

### Scene Regeneration

**Khi nào cần regenerate**:
- Video không đúng phong cách
- Nhân vật không nhất quán
- Chất lượng kém
- Nội dung không phù hợp

**Cách regenerate**:
1. Từ chối scene trong tab "Xem trước & phê duyệt"
2. Nhấn "Tạo lại scene này"
3. Hệ thống tạo video mới với cùng prompt
4. Xem lại và approve

### Auto-Upscale với Fallback

**Chiến lược thông minh**:
```
Try 1080p:
  ├─ Success → Download 1080p ✅
  └─ Failed:
       ├─ Timeout upscale → Fallback 720p ⚠️
       ├─ Upscale error → Fallback 720p ⚠️
       └─ Download error → Fallback 720p ⚠️
```

**Lợi ích**:
- Ưu tiên quality cao nhất (1080p)
- Đảm bảo luôn có video (fallback 720p)
- Không cần can thiệp thủ công

---

## 🔧 Cấu hình & Troubleshooting

### Cookies Configuration

**Lấy cookies từ browser**:
```bash
# Sử dụng tool có sẵn
python tools/extract_cookies.py

# File output: ./config/cookies.json
```

**Cookies bị hết hạn**:
- Đăng nhập lại Google Labs
- Extract cookies mới
- Update `cookies.json`

### API Key Issues

**API key không hợp lệ**:
- Kiểm tra key có đủ quyền Gemini API
- Tạo key mới tại: https://makersuite.google.com/app/apikey
- Lưu vào file `.txt` và upload lại

### Video Generation Failures

**Timeout khi tạo video**:
- VEO 3.1 đang quá tải → Thử lại sau
- Prompt quá phức tạp → Đơn giản hóa

**Không tạo được video**:
- Cookies hết hạn → Extract lại
- Prompt vi phạm policy → Sửa prompt
- Network issue → Kiểm tra internet

### Download Issues

**Upscale timeout**:
- Tăng timeout trong code (mặc định 5 phút)
- Hoặc chấp nhận 720p

**File không tải về**:
- Kiểm tra quyền ghi thư mục
- Kiểm tra dung lượng disk

---

## 📝 Best Practices

### 1. Kịch bản

✅ **Nên**:
- Chủ đề rõ ràng, cụ thể
- Mỗi scene 6-10 giây (tối ưu cho VEO)
- Prompt mô tả chi tiết visual, camera movement
- Nhất quán về style, lighting, character

❌ **Không nên**:
- Chủ đề quá chung chung
- Scene quá ngắn (< 3s) hoặc quá dài (> 15s)
- Prompt trừu tượng, không rõ ràng
- Thay đổi style giữa các scenes

### 2. Nhân vật

✅ **Nên**:
- Mô tả chi tiết: tuổi, giới tính, ngoại hình, trang phục
- Upload ảnh reference chất lượng cao, rõ mặt
- Giữ nhân vật nhất quán xuyên suốt

❌ **Không nên**:
- Mô tả mơ hồ: "một người"
- Ảnh mờ, góc nghiêng, khuất mặt
- Thay đổi nhân vật giữa chừng

### 3. Phê duyệt

✅ **Nên**:
- Xem kỹ từng scene trước khi approve
- Từ chối và tạo lại nếu không ưng
- Kiểm tra consistency giữa các scenes

❌ **Không nên**:
- Approve hết không xem
- Giữ lại scenes chất lượng kém
- Bỏ qua lỗi nhỏ (tích tụ thành lỗi lớn)

---

## 🚀 Quick Start Example

**Tạo video "Review iPhone 16" trong 10 phút**:

```bash
# Bước 1: Khởi động UI
./run_ui.sh

# Mở browser: http://localhost:7860
```

**Tab 1 - Khởi tạo**:
- Upload `api_key.txt`
- Tên dự án: `review_iphone16`
- Model: `gemini-2.0-flash-exp`
- → Khởi tạo

**Tab 2 - Kịch bản**:
- Chủ đề: "Review chi tiết iPhone 16 Pro Max - Camera, hiệu năng, pin"
- Thời lượng: 60s
- Mỗi cảnh: 8s
- Style: Cinematic
- Tỷ lệ: 16:9
- Nhân vật: AI tự nhận diện
- → Tạo kịch bản

**Tab 3 - SEO**:
- → Tạo nội dung SEO
- Copy nội dung để dùng sau

**Tab 4 - Tạo video**:
- Cookies: `./config/cookies.json`
- → Tạo tất cả video
- *(Đợi 5-10 phút)*

**Tab 5 - Phê duyệt**:
- Làm mới danh sách
- Xem từng scene
- Approve hoặc reject
- Regenerate nếu cần

**Tab 6 - Tải video**:
- Quality: 1080p
- → Tải tất cả video
- *(Đợi upscale + download)*

**Tab 7 - Nối video**:
- → Nối video
- **Hoàn thành!** 🎉

**File cuối**: `./data/projects/.../review_iphone16_final.mp4`

---

## 📚 Tài liệu liên quan

- [INSTALL_UI.md](INSTALL_UI.md) - Hướng dẫn cài đặt
- [DOWNLOAD_IMPLEMENTATION.md](DOWNLOAD_IMPLEMENTATION.md) - Chi tiết download workflow
- [VIDEO_PREVIEW_UI.md](VIDEO_PREVIEW_UI.md) - Preview UI specs
- [UI_READY.md](UI_READY.md) - Trạng thái UI hiện tại

---

**Phiên bản**: 1.0.0
**Cập nhật**: 2024-10-25
**Tác giả**: VEO 3.1 Automation Team
