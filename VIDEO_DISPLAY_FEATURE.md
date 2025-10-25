# 🎬 Video Display Feature - Implementation Complete!

## ✅ ĐÃ HOÀN THÀNH

Tool bây giờ có thể **hiển thị video ngay sau khi Flow tạo xong**!

---

## 🎯 Tính năng mới

### **1. Video Extraction từ Flow Page**

Sau khi video tạo xong, tool tự động:
- ✅ Tìm `<video>` element trên Flow page
- ✅ Extract video URL (Google Storage hoặc blob URL)
- ✅ Download video nếu là blob URL
- ✅ Lưu video vào `./data/videos/`

### **2. Video Display trong Gradio UI**

**Layout mới**:
```
Tab "Tạo Video (Comet)":
┌─────────────────────────────────┬─────────────────────────────────┐
│ 📋 Tiến trình sản xuất          │ 📸 Màn hình hiện tại (Comet)   │
│                                 │                                 │
│ 🎬 SCENE 1/7                    │                                 │
│ ⏳ Progress: 54% (65s)          │  [Live Screenshot]              │
│ ✅ Video đã tạo xong!            │                                 │
│ 📥 Video đã download:            │                                 │
│    ./data/videos/video_*.mp4   │                                 │
│                                 │                                 │
└─────────────────────────────────┴─────────────────────────────────┘
🎬 Video vừa tạo (Latest):
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│                    [VIDEO PLAYER - AUTOPLAY]                      │
│                                                                   │
│  ▶️  ═══════════════●─────────  0:05 / 0:08                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
📊 Trạng thái các cảnh: [JSON]
```

### **3. Automatic Download**

**3 phương pháp extraction**:

#### Method 1: Direct URL
```python
# Nếu Flow trả về direct URL (Google Storage)
video_url = "https://storage.googleapis.com/bucket/video.mp4"
return video_url  # Display directly
```

#### Method 2: Blob URL → Google Storage
```python
# Extract Google Storage URL từ page source
gcs_pattern = r'https://storage\.googleapis\.com/[^\s"\'<>]+'
matches = re.findall(gcs_pattern, page_html)
return matches[0]  # Return GCS URL
```

#### Method 3: Blob URL → Local Download
```python
# Download blob video via JavaScript
video_base64 = driver.execute_async_script("""
    fetch(blobUrl)
        .then(r => r.blob())
        .then(blob => {
            let reader = new FileReader();
            reader.onload = () => callback(reader.result);
            reader.readAsDataURL(blob);
        });
""", blob_url)

# Save to ./data/videos/video_TIMESTAMP.mp4
video_data = base64.b64decode(video_base64.split(',')[1])
with open(filepath, 'wb') as f:
    f.write(video_data)
```

---

## 🔧 Technical Implementation

### **File 1: `flow_controller_selenium.py`**

#### New Methods:

**1. `_extract_video_url()`**
```python
def _extract_video_url(self) -> Optional[str]:
    """
    Extract video URL from Flow page
    - Find <video> element
    - Get src attribute
    - Handle blob/direct URLs
    """
    video_elements = self.driver.find_elements(By.TAG_NAME, 'video')

    for video in video_elements:
        if video.is_displayed():
            src = video.get_attribute('src')

            if src.startswith('blob:'):
                # Try to convert or download
                actual_url = self._convert_blob_to_url(src)
                if not actual_url:
                    actual_url = self._download_blob_video(src)
                return actual_url
            else:
                return src  # Direct URL
```

**2. `_convert_blob_to_url()`**
```python
def _convert_blob_to_url(self, blob_url: str) -> Optional[str]:
    """
    Find Google Storage URL in page HTML
    """
    body_html = self.driver.page_source

    # Search for GCS URLs
    gcs_pattern = r'https://storage\.googleapis\.com/[^\s"\'<>]+'
    matches = re.findall(gcs_pattern, body_html)

    # Filter for video files
    video_matches = [m for m in matches if '.mp4' in m or 'video' in m]
    return video_matches[0] if video_matches else None
```

**3. `_download_blob_video()`**
```python
def _download_blob_video(self, blob_url: str) -> Optional[str]:
    """
    Download video from blob URL using JavaScript
    Returns local file path
    """
    # Execute async JS to fetch blob
    video_base64 = self.driver.execute_async_script("""
        let blobUrl = arguments[0];
        let callback = arguments[1];

        fetch(blobUrl)
            .then(r => r.blob())
            .then(blob => {
                let reader = new FileReader();
                reader.onload = () => callback(reader.result);
                reader.readAsDataURL(blob);
            });
    """, blob_url)

    # Decode and save
    video_data = base64.b64decode(video_base64.split(',')[1])
    filepath = f"./data/videos/video_{timestamp}.mp4"

    with open(filepath, 'wb') as f:
        f.write(video_data)

    return filepath  # Return local path for display
```

### **File 2: `RUN_WITH_COMET.py`**

#### UI Components:

**Video Player**:
```python
current_video = gr.Video(
    label="🎬 Video vừa tạo (Latest)",
    autoplay=True,  # Auto-play when video loads
    height=400
)
```

#### Workflow Updates:

**Track Latest Video**:
```python
latest_video = None  # Track latest generated video

# After video generation
if url:
    latest_video = url  # Update latest video

    # Log based on type
    if url.startswith('/') or url.startswith('./'):
        status_lines.append(f"   📥 Video đã download: {url}")
    else:
        status_lines.append(f"   🌐 Video URL: {url[:60]}...")

# Return video for display
return status_lines, scene_updates, current_screenshot, latest_video
```

**Event Handler**:
```python
produce_btn.click(
    fn=produce_videos_wrapper,
    inputs=[cookies_input],
    outputs=[
        production_output,    # Logs
        scene_status,         # Scene JSON
        current_scene_image,  # Screenshot
        current_video         # VIDEO PLAYER ← NEW!
    ]
)
```

---

## 🎬 User Experience

### **Workflow**:

1. **Tab 1: Tạo kịch bản**
   - Nhập chủ đề
   - Click "Tạo kịch bản"
   - Xem danh sách cảnh

2. **Tab 2: Tạo Video**
   - Click "Bắt đầu sản xuất"
   - **Comet window mở** (xem live)
   - **Gradio UI hiển thị**:
     - Logs real-time
     - Screenshots mỗi 10s
     - **VIDEO PLAYER** (sau khi tạo xong!)

3. **Sau mỗi video tạo xong**:
   - ✅ Video player tự động load
   - ✅ Autoplay video
   - ✅ Controls để pause/replay
   - ✅ Download button (native browser)

### **Example Flow**:

```bash
🎬 SCENE 1/7
   ⏳ Đang tạo video (VEO 3.1 - Comet)...
   ✅ Prompt filled
   🎬 Clicking Generate button...

   ⏳ Waiting for video generation...
      ⏳ Progress: 54% (65s / 120s)
      🎬 Flow progress: 57%
      ✅ Found play_arrow icon and no progress %
      ✅ Video generation completed!

      🔍 Finding video URL...
      Found video src: blob:https://labs.google/xyz...
      Blob URL detected, attempting to extract actual URL...
      Downloading video from blob URL...
      ✅ Video downloaded: ./data/videos/video_182345.mp4

   ✅ Video đã tạo xong!
   📥 Video đã download: ./data/videos/video_182345.mp4
   ✨ Scene 1: HOÀN THÀNH
```

**UI Updates**:
- Video player loads: `./data/videos/video_182345.mp4`
- Auto-plays 8-second video
- User can replay/download

---

## 📦 Files Modified

### **1. flow_controller_selenium.py**
**Changes**:
- ✅ `_extract_video_url()` - Main extraction method
- ✅ `_convert_blob_to_url()` - Find GCS URLs
- ✅ `_download_blob_video()` - Download blob via JS
- ✅ `create_video_from_prompt()` - Call extraction after generation

**Lines**: +130 lines

### **2. RUN_WITH_COMET.py**
**Changes**:
- ✅ `current_video` - Video player component
- ✅ `latest_video` tracking in `produce_videos_sync()`
- ✅ Output updates - Return video path
- ✅ Event handler - Output to video player

**Lines**: +20 lines

---

## 🎯 Supported Scenarios

### ✅ **Scenario 1: Google Storage URL**
```
Video src = https://storage.googleapis.com/bucket/video.mp4
→ Return URL directly
→ Display in video player
```

### ✅ **Scenario 2: Blob URL + GCS in HTML**
```
Video src = blob:https://labs.google/xyz
HTML contains: https://storage.googleapis.com/bucket/video.mp4
→ Extract GCS URL from HTML
→ Display in video player
```

### ✅ **Scenario 3: Blob URL Only**
```
Video src = blob:https://labs.google/xyz
No GCS URL found
→ Download blob via JavaScript
→ Save to ./data/videos/video_TIMESTAMP.mp4
→ Display local file in video player
```

---

## 📸 Screenshots Locations

```
./data/
├── logs/
│   ├── progress_182305.png       # Progress screenshots
│   ├── progress_182315.png
│   └── completed_182335.png      # Final screenshot
│
└── videos/
    ├── video_182345.mp4          # Downloaded videos
    ├── video_182420.mp4
    └── video_182501.mp4
```

---

## ⚙️ Configuration

**Video Settings**:
```python
# Gradio Video component
current_video = gr.Video(
    label="🎬 Video vừa tạo (Latest)",
    autoplay=True,      # Auto-play on load
    height=400,         # Player height
    # show_download_button=True  # Default enabled
)
```

**Download Directory**:
```python
download_dir = "./data/videos"  # Configurable in FlowController
```

---

## 🎉 Benefits

### **Trước**:
- ❌ Video chỉ trên Flow (không thấy được)
- ❌ Phải vào Flow manual để xem
- ❌ Không biết video như thế nào
- ❌ Không download được tự động

### **Sau**:
- ✅ Video hiển thị ngay trong UI
- ✅ Autoplay sau khi tạo xong
- ✅ Download tự động (nếu blob URL)
- ✅ Lưu local để reuse
- ✅ Preview trước khi assemble

---

## 🚀 How to Use

```bash
cd /Users/macos/Desktop/VEO2
source venv312/bin/activate
python RUN_WITH_COMET.py
```

Open: **http://localhost:7860**

**Workflow**:
1. Tab 1: Tạo kịch bản
2. Tab 2: Click "Bắt đầu sản xuất"
3. **Xem**:
   - Cột trái: Logs
   - Cột phải top: Screenshots
   - **Cột dưới: VIDEO PLAYER** ← NEW!
4. Video tự động play sau mỗi scene!

---

## 🎬 Demo Output

```
🎬 Video vừa tạo (Latest):
┌───────────────────────────────────────┐
│  [VIDEO PLAYING - 0:05 / 0:08]       │
│                                       │
│  Scene: Opening shot of kitchen      │
│  Model: Veo 3.1 - Fast               │
│  Duration: 8 seconds                  │
│                                       │
│  ▶️  ═══════════●────────              │
│                                       │
│  [Download] [Fullscreen]              │
└───────────────────────────────────────┘
```

---

## ✅ Summary

**Video Display Feature hoàn chỉnh**:
- ✅ Extract video URL từ Flow page
- ✅ Handle blob URLs (download tự động)
- ✅ Handle Google Storage URLs
- ✅ Display trong Gradio video player
- ✅ Autoplay sau khi tạo xong
- ✅ Lưu local vào ./data/videos/
- ✅ Native download controls

**Bạn bây giờ có thể**:
- Xem video ngay sau khi Flow tạo xong
- Không cần vào Flow manual
- Download tự động về máy
- Preview trước khi assemble final movie

**Tool sẵn sàng với video display!** 🎬🚀

---

*Feature complete: Video extraction and display implemented*
