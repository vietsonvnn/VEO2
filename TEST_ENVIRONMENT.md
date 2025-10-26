# 🧪 TEST ENVIRONMENT - VEO 3.1

## Môi trường test sạch để kiểm tra app mới

### 📋 Checklist Trước Khi Test

#### 1. Clean Up Environment
```bash
# Kill tất cả Python processes cũ
pkill -9 python
pkill -9 Python

# Hoặc kill specific processes
ps aux | grep python | grep -v grep | awk '{print $2}' | xargs kill -9

# Verify port 7860 trống
lsof -ti:7860
# Nếu có process → kill nó
lsof -ti:7860 | xargs kill -9
```

#### 2. Verify Dependencies
```bash
# Activate venv
source venv312/bin/activate

# Check Python version
python --version  # Should be 3.12.x

# Verify packages
pip list | grep -E "playwright|gradio|google-generativeai"
```

#### 3. Check Files Exist
```bash
# Core files
ls -lh app.py flow_video_tracker.py

# Config files
ls -lh config/cookies.json .env

# Verify cookies valid (created within last 7 days)
stat -f "%Sm" config/cookies.json
```

---

## 🚀 Start App

### Method 1: Direct Start (Recommended for testing)
```bash
cd /Users/macos/Desktop/VEO2
source venv312/bin/activate
python app.py
```

**Expected Output:**
```
============================================================
🎬 VEO 3.1 - Production Tool (ELECTRON VERSION)
============================================================
✨ Card-based UI
🚀 Electron Browser (Playwright)
🎯 Output = 1 video per prompt
📍 Baseline URL Tracking (100% accurate)
🔄 Regenerate videos
🗑️  Delete videos from Flow
📊 Log collapsed at bottom
============================================================
🌐 http://localhost:7860
============================================================
Running on local URL:  http://127.0.0.1:7860
```

### Method 2: Background Mode
```bash
# Start in background
nohup python app.py > app.log 2>&1 &

# Get PID
echo $!

# Monitor logs
tail -f app.log

# Stop when done
kill <PID>
```

---

## 🧪 Test Workflow

### Step 1: Verify UI Loads
1. Open browser: http://localhost:7860
2. Check UI elements visible:
   - ✅ Topic input
   - ✅ Duration slider
   - ✅ API Key field
   - ✅ Project ID field
   - ✅ Cookies path field
   - ✅ **NEW: Aspect Ratio radio (16:9 / 9:16)**
   - ✅ **NEW: Model dropdown (Veo 3.1 Fast / Quality)**
   - ✅ Generate Script button
   - ✅ Create Videos button

### Step 2: Test Script Generation
1. **Topic**: "Làm bánh mì Việt Nam"
2. **Duration**: 1 phút
3. **Aspect Ratio**: Chọn 16:9 hoặc 9:16
4. **Model**: Chọn Veo 3.1 - Fast hoặc Quality
5. Click "📝 1. Tạo kịch bản"

**Expected:**
```
✅ Hướng dẫn làm bánh mì Việt Nam
📝 [Description]
🎬 2-3 cảnh
📐 Tỷ lệ: 16:9
🎨 Model: Veo 3.1 - Fast
```

### Step 3: Test Video Creation
1. Click "🎬 2. Tạo videos"
2. Monitor log output:
   - ✅ Browser khởi động
   - ✅ Vào project
   - ✅ **NEW: Set aspect ratio**
   - ✅ **NEW: Set model**
   - ✅ Set output = 1
   - ✅ Tạo videos (instant fill, không type chậm)
   - ✅ Videos hiển thị trong cards

**Check Performance:**
- **Input Speed**: <1 giây per prompt (instant fill)
- **Settings Applied**: Verify trong log
- **Video Matching**: Mỗi scene có đúng video URL

### Step 4: Test Regenerate
1. Click button **🔄 Tạo lại** trên 1 card
2. Verify:
   - ✅ Browser mở lại
   - ✅ Settings applied
   - ✅ Video mới được tạo
   - ✅ Card update với video mới

### Step 5: Test Delete
1. Click button **🗑️ Xóa** trên 1 card
2. Verify:
   - ✅ Browser mở
   - ✅ Video deleted from Flow project
   - ✅ Card removed from UI
   - ✅ Scenes renumbered

---

## 🎯 Test Cases

### A. Settings Test

#### Test Case 1: Aspect Ratio 16:9
- Select: 16:9 (Khổ ngang)
- Create video
- **Expected**: Video landscape format

#### Test Case 2: Aspect Ratio 9:16
- Select: 9:16 (Khổ dọc)
- Create video
- **Expected**: Video portrait format (TikTok/Reels style)

#### Test Case 3: Model Fast
- Select: Veo 3.1 - Fast
- Create video
- **Expected**: Faster generation, good quality

#### Test Case 4: Model Quality
- Select: Veo 3.1 - Quality
- Create video
- **Expected**: Slower generation, higher quality

### B. Performance Test

#### Test Case 5: Input Speed
- Create script với 3 scenes
- Monitor log for "Filling prompt" time
- **Expected**: <1s per prompt (instant fill)
- **Before**: ~10s per prompt (type with delay)

### C. Full Workflow Test

#### Test Case 6: Complete Flow
1. Topic: "Nấu phở bò"
2. Duration: 1.5 phút
3. Aspect: 16:9
4. Model: Veo 3.1 - Fast
5. Generate script
6. Create videos
7. Regenerate scene 2
8. Delete scene 1
9. Verify results

**Success Criteria:**
- ✅ All videos created
- ✅ Settings applied correctly
- ✅ Regenerate works
- ✅ Delete works
- ✅ UI updates correctly

---

## 📊 Expected Logs

### Normal Flow:
```
INFO:flow_video_tracker:🚀 Starting Flow Video Tracker...
INFO:flow_video_tracker:🌐 Navigating to Flow...
INFO:flow_video_tracker:✅ Browser ready
INFO:flow_video_tracker:📁 Going to project...
INFO:flow_video_tracker:✅ Project loaded
INFO:flow_video_tracker:⚙️  Configuring: Output count = 1...
INFO:flow_video_tracker:   ✅ Set to 1!
INFO:flow_video_tracker:⚙️  Setting aspect ratio: 16:9...
INFO:flow_video_tracker:   ✅ Set to 16:9 (Landscape)
INFO:flow_video_tracker:⚙️  Setting model: Veo 3.1 - Fast...
INFO:flow_video_tracker:   ✅ Set to Veo 3.1 - Fast
INFO:flow_video_tracker:🎬 Creating 3 videos...
INFO:flow_video_tracker:📹 SCENE 1/3
INFO:flow_video_tracker:   ✍️  Filling prompt...
INFO:flow_video_tracker:   🎯 Clicking Generate...
INFO:flow_video_tracker:   ✅ Clicked Generate
INFO:flow_video_tracker:   👀 Waiting for video...
INFO:flow_video_tracker:   ✅ Found 1 new video(s)!
INFO:flow_video_tracker:✅ Scene 1 completed!
```

### Error Scenarios:

**Cookies Invalid:**
```
ERROR: Failed to load cookies
```
→ Re-export cookies from Flow

**Project Not Found:**
```
ERROR: Failed to navigate to project
```
→ Check project ID in URL

**Settings Failed:**
```
⚠️  Settings error: [error message]
```
→ Check Flow UI, may have changed

---

## 🐛 Troubleshooting

### Issue 1: Port 7860 Already in Use
```bash
# Find and kill process
lsof -ti:7860 | xargs kill -9

# Or use different port
GRADIO_SERVER_PORT=7861 python app.py
```

### Issue 2: Browser Not Opening
```bash
# Check Playwright installation
playwright install chromium

# Test browser
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=False); b.close(); p.stop()"
```

### Issue 3: Cookies Expired
```bash
# Re-export cookies
# 1. Go to Flow in Chrome
# 2. Open DevTools → Application → Cookies
# 3. Export using cookie extension
# 4. Save to config/cookies.json
```

### Issue 4: Settings Not Applied
- Check Flow UI hasn't changed
- Enable logging: `logger.setLevel(logging.DEBUG)`
- Check screenshots in debug mode
- Verify selectors in Setting_Intro.txt

---

## 📁 Test Files Structure

```
VEO2/
├── app.py                          # Main Gradio app
├── flow_video_tracker.py           # Core engine
├── config/
│   └── cookies.json               # Flow cookies
├── .env                            # API keys
├── test_ui_workflow.py            # Quick test script
└── TEST_ENVIRONMENT.md            # This file
```

---

## ✅ Success Indicators

App hoạt động tốt khi:

1. **UI**: Loads without errors
2. **Script Gen**: Creates scenes with correct prompts
3. **Settings**: Displays selected aspect ratio & model
4. **Video Creation**:
   - Input instant (<1s)
   - Settings applied
   - Videos created correctly
5. **Regenerate**: Works and updates card
6. **Delete**: Removes video from Flow + UI
7. **Performance**: Fast, no crashes

---

## 🎬 Quick Start Command

```bash
# One-liner để start clean
cd /Users/macos/Desktop/VEO2 && \
pkill -9 python 2>/dev/null; \
lsof -ti:7860 | xargs kill -9 2>/dev/null; \
source venv312/bin/activate && \
python app.py
```

Happy Testing! 🚀
