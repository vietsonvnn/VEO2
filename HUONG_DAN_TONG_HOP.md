# HƯỚNG DẪN TỔNG HỢP - GOOGLE LABS FLOW VIDEO AUTOMATION

> Tài liệu tổng hợp đầy đủ về quy trình tạo, quản lý và tải video từ Google Labs Flow

---

## 📋 MỤC LỤC

1. [Quy trình Login](#1-quy-trình-login)
2. [Quy trình Tạo Video](#2-quy-trình-tạo-video)
3. [Theo dõi Tiến trình Tạo Video](#3-theo-dõi-tiến-trình-tạo-video)
4. [Quy trình Download](#4-quy-trình-download)
5. [Giải pháp Hiển thị Video](#5-giải-pháp-hiển-thị-video)
6. [Buttons và Selectors](#6-buttons-và-selectors)
7. [Full Selectors Reference](#7-full-selectors-reference)
8. [Video Play Controls](#8-video-play-controls)
9. [Requirements](#9-requirements)

---

## 1. QUY TRÌNH LOGIN

### Tổng quan
**Login vào Flow là OAuth Google, không phải đăng ký riêng.**

### Quy trình chi tiết

**Bước 1: Trang chính Lab FX**
- URL: `https://labs.google/fx`
- Các sản phẩm: Flow, Whisk, ImageFX, MusicFX
- Nút: **"Sign in with Google" / "Đăng nhập bằng Google"**

**Bước 2: OAuth Google**
1. Click "Sign in with Google" hoặc "Launch Flow"
2. Popup/chuyển hướng đến: `https://accounts.google.com/o/oauth2/auth`
3. Nhập email & mật khẩu Google
4. Xác thực 2 bước (nếu có)

**Bước 3: Sau khi xác thực thành công**
- Trả về access token/ID token
- Chuyển về: `https://labs.google/fx/vi/tools/flow`
- Session lưu qua cookie/localStorage

### Giao diện sau login
- Header hiển thị email đăng nhập (VD: guagency014@test.guagency.io.vn)
- Các nút:
  - Thêm tín dụng AI
  - Thư viện của tôi
  - Quản lý gói thuê bao
  - Quyền riêng tư
  - Điều khoản dịch vụ

### Network/API
- GET đến Google OAuth endpoint
- POST access token về backend Flow
- Session kiểm tra: user_id, email, credits, subscription

---

## 2. QUY TRÌNH TẠO VIDEO

### BƯỚC 1: Nhập Prompt

**Element:**
- **Type:** Textarea
- **Selector:** `textarea[node="72"]`
- **Placeholder:** "Tạo một video bằng văn bản…"

```javascript
await page.fill('textarea[node="72"]', 'A beautiful sunset over mountains');
```

### BƯỚC 2: Cấu hình Settings (Optional)

#### 2.1. Chọn Mode
- **Text:** "Từ văn bản sang video"
- **Icon:** `arrow_drop_down`
- **Selector:** `select[node="246"]`
- **Options:**
  - Từ văn bản sang video
  - Tạo video từ các khung hình
  - Tạo video từ các thành phần

#### 2.2. Chọn Model
- **Text:** "Veo 3.1 - Quality"
- **Options:**
  - Veo 3.1 - Fast (Beta Audio)
  - Veo 3.1 - Quality (Beta Audio) ⭐ Default
  - Veo 2 - Fast (Support Ending Soon)
  - Veo 2 - Quality (Support Ending Soon)

#### 2.3. Chọn Aspect Ratio
- **Icon:** `crop_16_9` hoặc `crop_portrait`
- **Options:**
  - Khổ ngang (16:9)
  - Khổ dọc (9:16)

#### 2.4. Chọn Output Count
- **Icon:** `x1`, `x2`, `x3`, `x4`
- **Options:** 1, 2, 3, hoặc 4 videos

### BƯỚC 3: Generate Video

**Element:**
- **Text:** "Tạo"
- **Icon:** `arrow_forward`
- **Selector:** `button:has-text("Tạo")`

```javascript
await page.click('button:has-text("Tạo")');
```

### BƯỚC 4: Loading State

```html
<div class="generation-status">
  <div class="loading-spinner"></div>
  <p>Đang tải...</p>
  <div class="progress-bar">
    <div class="progress-fill" style="width: 45%"></div>
  </div>
  <p class="eta">Ước tính: 2 phút 30 giây</p>
</div>
```

### BƯỚC 5: Video Card Display

Khi video hoàn thành:

```html
<div class="video-result-card">
  <div class="video-header">
    <div class="video-date">25 thg 10, 2025</div>
    <button class="btn-icon">
      <span id="playIcon">play_arrow</span>
      <span id="duration">0:08</span>
    </button>
  </div>

  <div class="video-player-container">
    <video src="{video-url}"></video>
  </div>

  <div class="video-info">
    <h4>Nhập câu lệnh</h4>
    <p class="prompt-text">A beautiful sunset over mountains</p>
    <p class="model-badge">Veo 3.1 - Quality</p>
  </div>

  <div class="video-actions">
    <button>Tải xuống</button>
    <button>Chỉnh sửa</button>
    <button>Chèn</button>
    <button>Gắn cờ</button>
    <button>Xoá</button>
  </div>
</div>
```

---

## 3. THEO DÕI TIẾN TRÌNH TẠO VIDEO

### Cách theo dõi Progress Bar

**Thông tin hiển thị:**
- Ngày tháng: "25 thg 10, 2025"
- Phần trăm: `3%`, `9%`, `15%`, `21%`, `33%`, `45%`, `57%`... đến 100%
- Model name: "Veo 3.1 - Fast"

### Automation Code

```python
while True:
    # Tìm element chứa "%"
    progress_element = find_element_with_text("%")

    if progress_element:
        # Extract số %
        progress = extract_number(progress_element.text)
        print(f"Progress: {progress}%")
    else:
        # Không còn % = hoàn thành
        break

    time.sleep(2)  # Đợi 2 giây rồi check lại
```

### Kiểm tra kết quả

**Trường hợp 1: Thành công ✅**
- Video player với icon `play_arrow`
- Thời lượng: "0:08"
- Tiêu đề: "Nhập câu lệnh"
- Prompt đã nhập
- Model name: "Veo 3.1 - Fast"

**Trường hợp 2: Thất bại ❌**
- Text: **"Không tạo được"**
- Vẫn có icon và thời lượng
- Vẫn hiển thị prompt và model name

### Các Selector Quan Trọng

| Element | Cách tìm | Ý nghĩa |
|---------|----------|---------|
| Progress | Text chứa `%` | Đang xử lý |
| Video player | Icon `play_arrow` | Video đã sẵn sàng |
| Duration | Text pattern `0:08` | Thời lượng video |
| Error | Text `Không tạo được` | Tạo thất bại |
| Model name | Text `Veo 3.1 - Fast` | Xác nhận mô hình |

---

## 4. QUY TRÌNH DOWNLOAD

### BƯỚC 1: Mở Menu Download

**Element:**
- **Text:** "Tải xuống"
- **Selector:** `button:has-text("Tải xuống")`

```javascript
await page.click('button:has-text("Tải xuống")');
```

### BƯỚC 2: Chọn Độ Phân Giải (3 Options)

#### Option 1: Ảnh GIF động (270p)
- **Text:** "Ảnh GIF động (270p)"
- **Icon:** `gif_box`
- **Selector:** `menuitem:has-text("Ảnh GIF động (270p)")`
- **Output:** File GIF animated
- **Download:** Ngay lập tức
- **Use case:** Preview, chia sẻ nhanh

#### Option 2: Kích thước gốc (720p)
- **Text:** "Kích thước gốc (720p)"
- **Icon:** `capture`
- **Selector:** `menuitem:has-text("Kích thước gốc (720p)")`
- **Output:** Video MP4 720p
- **Download:** Ngay lập tức
- **Use case:** Sử dụng thông thường

#### Option 3: Đã tăng độ phân giải (1080p) ⭐
- **Text:** "Đã tăng độ phân giải (1080p)"
- **Icon:** `aspect_ratio`
- **Selector:** `menuitem:has-text("Đã tăng độ phân giải (1080p)")`
- **Output:** Video MP4 1080p
- **Download:** Sau khi upscale (1-3 phút)
- **Use case:** Chất lượng cao, production

### BƯỚC 3: Chờ Upscale (Chỉ với 1080p)

**Notification xuất hiện:**

```html
<li>
  Đang tăng độ phân giải cho video của bạn (không mất tín dụng).
  Quá trình này có thể mất vài phút.
  <button>Đóng</button>
</li>
```

**Selector:**
```javascript
await page.waitForSelector('li:has-text("Đang tăng độ phân giải")');
```

**Khi hoàn tất:**

```html
<li>
  check_circle
  Đã xong việc tăng độ phân giải!
  Tải xuống
  <button>Đóng</button>
</li>
```

**Selector:**
```javascript
await page.waitForSelector('li:has-text("Đã xong việc tăng độ phân giải!")');
```

### BƯỚC 4: Download File

```javascript
// Setup download handler
const downloadPromise = page.waitForEvent('download');

// Click download trong notification
await page.locator('li:has-text("Đã xong việc tăng độ phân giải!")')
  .locator('text=Tải xuống')
  .click();

// Chờ download
const download = await downloadPromise;
await download.saveAs('./videos/output.mp4');
```

### Bảng Tổng Hợp Download Options

| Tính năng | Chi tiết |
|-----------|----------|
| Số options | 3 (GIF 270p, MP4 720p, MP4 1080p) |
| Download ngay | MP4 720p (instant) |
| Cần xử lý | GIF (vài giây), 1080p (1-3 phút) |
| Notification | Real-time với spinner → success + download button |
| Chi phí | Tất cả FREE (không mất tín dụng) |
| API | REST với polling mechanism |

---

## 5. GIẢI PHÁP HIỂN THỊ VIDEO

### Giải pháp 1: Veo 3.1 API ⭐⭐⭐ (Tốt nhất)

#### A. Gemini API (Đơn giản)

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="veo-3.1-generate-preview",
    contents="A beautiful sunset over the ocean"
)

video_url = response.video_url
print(f"Video URL: {video_url}")
```

#### B. Vertex AI (Enterprise)

```python
from vertexai.preview.vision_models import VideoGenerationModel

model = VideoGenerationModel.from_pretrained("veo-3.1-generate-preview")
response = model.generate_videos(
    prompt="A beautiful sunset over the ocean",
    aspect_ratio="16:9",
    duration_seconds=8
)

video_uri = response.videos[0].gcs_uri
```

**Ưu điểm:**
- ✅ Chính thức từ Google
- ✅ Không cần scrape Flow UI
- ✅ Có thể tạo video trực tiếp
- ✅ Lấy URL video dễ dàng

**Nhược điểm:**
- ❌ Cần API key/GCP project
- ❌ Có thể tốn phí

### Giải pháp 2: Intercept Network ⭐⭐

```python
from playwright.sync_api import sync_playwright

def capture_flow_video():
    video_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):
            content_type = response.headers.get('content-type', '')

            if 'video' in content_type or response.url.endswith('.mp4'):
                print(f"✅ Found video: {response.url}")
                video_urls.append(response.url)

            if 'storage.googleapis.com' in response.url:
                print(f"📦 GCS URL: {response.url}")
                video_urls.append(response.url)

        page.on("response", handle_response)

        # Login và tạo video...

        return video_urls
```

### Giải pháp 3: Extract Blob URL ⭐

```javascript
// Lấy video src
video_src = driver.execute_script("""
    let video = document.querySelector('video');
    return video ? video.src : null;
""")

// Convert blob to base64
video_base64 = driver.execute_async_script("""
    let video = document.querySelector('video');
    let callback = arguments[0];

    fetch(video.src)
        .then(r => r.blob())
        .then(blob => {
            let reader = new FileReader();
            reader.onload = () => callback(reader.result);
            reader.readAsDataURL(blob);
        })
""")
```

### So sánh Giải pháp

| Giải pháp | Độ khó | Chi phí | Chất lượng | Khuyến nghị |
|-----------|--------|---------|------------|-------------|
| **Veo 3.1 API** | Trung bình | Có phí | Cao nhất | ⭐⭐⭐ |
| **Network Intercept** | Khó | Miễn phí | Cao | ⭐⭐ |
| **Blob Extract** | Trung bình | Miễn phí | Cao | ⭐⭐ |

---

## 6. BUTTONS VÀ SELECTORS

### Button "+ Dự án mới"

**Cơ chế:**
1. Generate UUID mới cho project
2. Navigate sang `/project/{UUID}`
3. Render empty project editor

```javascript
function createNewProject() {
  const projectId = generateUUID();

  const newProject = {
    id: projectId,
    title: '',
    createdAt: new Date().toISOString(),
    videos: [],
    settings: {
      aspectRatio: '16:9',
      outputCount: 1,
      model: 'veo-3.1-quality'
    }
  };

  localStorage.setItem('video-projects', JSON.stringify([newProject]));
  window.location.href = `/project.html?id=${projectId}`;
}
```

### Các Button Chính

**1. Button Generate/Tạo**
- **Selector:** `button:contains("Tạo")`
- **Icon:** `arrow_forward`
- **Chức năng:** Sinh video/flow

**2. Button Cài đặt/Mở rộng**
- **Selector:** `button:has-text("Cài đặt")`
- **Icon:** `pen_spark`
- **Chức năng:** Mở tuỳ chỉnh cảnh/video

**3. Select Video Type**
- **Selector:** `select[node="246"]`
- **Text:** "Từ văn bản sang video"
- **Type:** Combobox

**4. Button More Options**
- **Selector:** `button:has-text("more_vert")`
- **Icon:** `more_vert` (ba chấm dọc)
- **Chức năng:** Menu tuỳ chọn

### Button Sau Khi Tạo Video

**5. Play/Pause**
- **Selector:** `button[aria-label*="play"]`
- **Icon:** `play_arrow` / `pause`

**6. Timeline/Progress**
- **Text:** Thời lượng (VD: "0:08")
- **Vị trí:** Dưới video player

**7. More Options**
- **Icon:** `more_vert`
- **Menu:** Download, Share, Delete, Rename, Copy link

**8. Video Card**
- **Text:** "Nhập câu lệnh" + prompt
- **Info:** Ngày tạo, thời lượng, model

---

## 7. FULL SELECTORS REFERENCE

### Popup 3 Options Quality

**Popup Container:**
```css
menu[aria-label="download Tải xuống"]
menu[aria-current="true"]
```

**Button GIF 270p:**
```html
<menuitem node="12683">
  gif_box<br/>Ảnh GIF động (270p)
</menuitem>
```
```css
menuitem:has-text("Ảnh GIF động (270p)")
```

**Button 720p:**
```html
<menuitem node="12684">
  capture<br/>Kích thước gốc (720p)
</menuitem>
```
```css
menuitem:has-text("Kích thước gốc (720p)")
```

**Button 1080p:**
```html
<menuitem node="12685">
  aspect_ratio<br/>Đã tăng độ phân giải (1080p)
</menuitem>
```
```css
menuitem:has-text("Đã tăng độ phân giải (1080p)")
```

### Notification Upscale

**Container:**
```css
section[aria-label="Notifications alt+T"]
section[aria-live="polite"]
```

**Processing Notification:**
```html
<li>
  Đang tăng độ phân giải cho video của bạn (không mất tín dụng).
  Quá trình này có thể mất vài phút.
  <button>Đóng</button>
</li>
```
```css
li:has-text("Đang tăng độ phân giải")
```

**Success Notification:**
```html
<li>
  check_circle<br/>
  Đã xong việc tăng độ phân giải!
  Tải xuống
  <button>Đóng</button>
</li>
```
```css
li:has-text("Đã xong việc tăng độ phân giải!")
```

**Download Link:**
```javascript
await page.locator('li:has-text("Đã xong")')
  .locator('text=Tải xuống')
  .click();
```

### Bảng Tổng Hợp Selectors

| Element | Text | Selector |
|---------|------|----------|
| Popup container | - | `menu[aria-label="download Tải xuống"]` |
| Button GIF 270p | "Ảnh GIF động (270p)" | `menuitem:has-text("Ảnh GIF động (270p)")` |
| Button 720p | "Kích thước gốc (720p)" | `menuitem:has-text("Kích thước gốc (720p)")` |
| Button 1080p | "Đã tăng độ phân giải (1080p)" | `menuitem:has-text("Đã tăng độ phân giải (1080p)")` |
| Notification container | - | `section[aria-label="Notifications alt+T"]` |
| Processing notification | "Đang tăng độ phân giải..." | `li:has-text("Đang tăng độ phân giải")` |
| Success notification | "Đã xong việc tăng độ phân giải!" | `li:has-text("Đã xong việc tăng độ phân giải!")` |
| Download link | "Tải xuống" | `li:has-text("Đã xong") >> text=Tải xuống` |
| Close button | "Đóng" | `button:has-text("Đóng")` |

---

## 8. VIDEO PLAY CONTROLS

### Play/Pause Button

**States:**
| Trạng thái | Icon | Hành động |
|------------|------|-----------|
| Paused | `play_arrow` ▶ | video.play() |
| Playing | `pause` ⏸ | video.pause() |
| Ended | `replay` 🔄 | video.currentTime = 0; play() |

### Video Player Structure

```html
<div class="video-player-container">
  <!-- Video element -->
  <video
    id="generatedVideo"
    src="{video-url}"
    playsinline
    controls
  ></video>

  <!-- Large play overlay -->
  <div class="play-overlay" onclick="togglePlay()">
    <button class="btn-play-large">
      <span class="material-icons">play_arrow</span>
    </button>
  </div>
</div>
```

### Player Controls

```javascript
class VideoPlayer {
  constructor(videoElement) {
    this.video = videoElement;
    this.isPlaying = false;
    this.setupEventListeners();
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    this.video.play();
    this.isPlaying = true;
    document.getElementById('playIcon').textContent = 'pause';
  }

  pause() {
    this.video.pause();
    this.isPlaying = false;
    document.getElementById('playIcon').textContent = 'play_arrow';
  }

  updateProgress() {
    const current = this.formatTime(this.video.currentTime);
    const total = this.formatTime(this.video.duration);
    document.getElementById('duration').textContent =
      `${current} / ${total}`;
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
}
```

### Cách Play Video

1. Click nút Play mini (header) - `play_arrow` icon
2. Click large overlay button giữa video
3. Click anywhere trên video
4. Keyboard: Spacebar (khi focus)

### Built-in HTML5 Controls

- ▶/⏸ Play/Pause
- Progress bar với seek
- 🔊 Volume control
- ⏯ Timeline scrubbing
- ⛶ Fullscreen button

---

## 9. REQUIREMENTS

### Python Dependencies

```txt
# Core dependencies
playwright>=1.48.0
google-generativeai>=0.8.3
python-dotenv>=1.0.1
pyyaml>=6.0.2

# Video processing
moviepy==1.0.3
opencv-python==4.10.0.84

# Web UI
gradio==4.44.0

# Python 3.14 compatibility
numpy>=1.24.0

# Utilities
requests==2.32.3
aiohttp==3.10.10
tqdm==4.66.5
```

### Cookies Configuration

Các cookies cần thiết cho authentication:

```json
[
  {
    "name": "EMAIL",
    "value": "guagency014@test.guagency.io.vn",
    "domain": "labs.google"
  },
  {
    "name": "__Host-next-auth.csrf-token",
    "domain": "labs.google",
    "httpOnly": true,
    "secure": true
  },
  {
    "name": "__Secure-next-auth.session-token",
    "domain": "labs.google",
    "httpOnly": true,
    "secure": true
  }
]
```

---

## 📊 CODE MẪU HOÀN CHỈNH

### Full Automation Script

```javascript
const { chromium } = require('playwright');

async function createAndDownloadFlowVideo(prompt, outputPath) {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    acceptDownloads: true
  });
  const page = await context.newPage();

  try {
    console.log('🚀 Bắt đầu quy trình tạo video...');

    // 1. Navigate to Flow
    await page.goto('https://labs.google/fx/vi/tools/flow');

    // 2. Nhập prompt
    console.log('📝 Nhập prompt:', prompt);
    await page.fill('textarea[node="72"]', prompt);
    await page.waitForTimeout(500);

    // 3. Click Generate
    console.log('⚡ Generate video...');
    await page.click('button:has-text("Tạo")');

    // 4. Chờ video được tạo
    console.log('⏳ Chờ video được tạo...');
    await page.waitForSelector('button[aria-label*="play"]', {
      timeout: 120000
    });
    console.log('✅ Video đã được tạo xong');

    // 5. Mở menu download
    console.log('📥 Mở menu download...');
    await page.click('button:has-text("Tải xuống")');
    await page.waitForTimeout(1000);

    // 6. Chọn 1080p
    console.log('🎬 Chọn độ phân giải 1080p...');
    await page.click('menuitem:has-text("Đã tăng độ phân giải (1080p)")');

    // 7. Chờ upscale
    console.log('⏳ Chờ upscale 1080p...');
    await page.waitForSelector('li:has-text("Đang tăng độ phân giải")');

    let isUpscaling = true;
    let attempts = 0;
    const maxAttempts = 60;

    while (isUpscaling && attempts < maxAttempts) {
      await page.waitForTimeout(5000);
      const notification = await page.$('li:has-text("Đang tăng độ phân giải")');
      if (!notification) {
        isUpscaling = false;
      }
      attempts++;

      if (attempts % 6 === 0) {
        console.log(`⏳ Đã chờ ${attempts * 5} giây...`);
      }
    }

    console.log('✅ Upscale hoàn tất');
    await page.waitForTimeout(2000);

    // 8. Download file
    console.log('📥 Tải video về máy...');
    const downloadPromise = page.waitForEvent('download');

    await page.locator('li:has-text("Đã xong việc tăng độ phân giải!")')
      .locator('text=Tải xuống')
      .click();

    const download = await downloadPromise;
    await download.saveAs(outputPath);

    console.log('✅ Đã tải video về:', outputPath);
    return outputPath;

  } catch (error) {
    console.error('❌ Lỗi:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

// Sử dụng
createAndDownloadFlowVideo(
  'cherry blossom in spring',
  './videos/cherry-blossom.mp4'
);
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Timing & Waiting
- Video generation: 30s - 2 phút
- Upscale 1080p: 1-5 phút
- Luôn có wait time hợp lý giữa các bước

### Multiple Videos
- Xác định đúng video card bằng prompt text
- Video mới nhất thường ở đầu danh sách

### Error Handling
- Xử lý timeout khi generation quá lâu
- Xử lý trường hợp upscale fail
- Retry logic cho network issues

### Selectors
- Selector dựa text có thể thay đổi theo ngôn ngữ
- `button:has-text("Tải xuống")` xuất hiện 2 lần (step 5 & 8)
- Phân biệt bằng timing/context

### Authentication
- Cần đăng nhập Google account
- Browser context phải có cookies/session
- Có thể cần xử lý 2FA

### Rate Limits
- Google Labs có giới hạn số video/ngày
- Không spam generate quá nhiều
- Có credit/quota system

---

## 🎯 FLOWCHART QUY TRÌNH

```
START
  ↓
[1. Nhập Prompt] → textarea[node="72"]
  ↓
[2. Config (Optional)] → Model/Type/Aspect Ratio
  ↓
[3. Click Generate] → button:has-text("Tạo")
  ↓
[4. Chờ Video Xong] → Wait for play button
  ↓
[5. Mở Menu Download] → button:has-text("Tải xuống") #1
  ↓
[6. Chọn 1080p] → menuitem:has-text("...1080p)")
  ↓
[7. Chờ Upscale] → Wait for notification gone
  ↓
[8. Download File] → li >> text=Tải xuống
  ↓
END (File saved to disk)
```

---

## 📚 NGUỒN THAM KHẢO

- Google Labs Flow: https://labs.google/fx/tools/flow
- Veo 3.1 API Docs: https://ai.google.dev/gemini-api/docs
- Vertex AI Video: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation
- Playwright Docs: https://playwright.dev

---

**Tài liệu được tổng hợp từ thư mục Huong Dan**
*Cập nhật: 2025-10-26*
