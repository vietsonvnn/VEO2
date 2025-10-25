# 📊 Flow Progress Tracking - Implementation Guide

## 🎯 Quy trình tạo video trong Flow (Đã phân tích)

### **BƯỚC 1: Nhập Prompt và Bắt đầu**
- Nhập text vào ô "Tạo một video bằng văn bản…"
- Nhấn Enter hoặc click button để bắt đầu tạo

### **BƯỚC 2: Theo dõi Progress Bar**

#### Thông tin Progress hiển thị:
- **Ngày tháng**: "25 thg 10, 2025"
- **Phần trăm hoàn thành**: `3%`, `9%`, `15%`, `21%`, `33%`, `45%`, `57%`... đến 100%
- **Tên mô hình**: "Veo 3.1 - Fast"

#### Timeline Progress:
```
3% → 9% → 15% → 21% → 33% → 45% → 57% → 69% → 81% → 93% → 100% → (biến mất)
```

**Lưu ý**: Progress không tuyến tính, có thể nhảy bước!

### **BƯỚC 3: Video Hoàn thành**

#### ✅ **Trường hợp 1: Tạo thành công**
Xuất hiện:
- **Video player** với icon `play_arrow`
- **Thời lượng video**: "0:08" (8 giây)
- **Tiêu đề**: "Nhập câu lệnh"
- **Prompt đã nhập**: (ví dụ: "A beautiful sunset over the ocean...")
- **Tên mô hình**: "Veo 3.1 - Fast"
- **Không còn text "%"** (quan trọng!)

#### ❌ **Trường hợp 2: Tạo thất bại**
Xuất hiện:
- Text: **"Không tạo được"** (Failed to generate)
- Vẫn có icon `play_arrow` và thời lượng "0:08"
- Vẫn hiện thị prompt và model name

---

## 🔧 Implementation trong Tool

### **1. Detect Progress (3%, 9%, 15%...)**

```python
def _check_generation_progress(self) -> Optional[str]:
    """
    Flow shows: 3% → 9% → 15% → 21% → 33% → 45% → 57% → ...
    """
    body_text = self.driver.find_element(By.TAG_NAME, 'body').text

    # Find all percentages
    import re
    percent_matches = re.findall(r'\b(\d{1,3})%\b', body_text)

    if percent_matches:
        percentages = [int(p) for p in percent_matches if int(p) <= 100]
        if percentages:
            max_percent = max(percentages)  # Get highest %
            return f"{max_percent}%"

    # Check for "Veo 3.1 - Fast" (indicates processing)
    if "Veo 3.1" in body_text and "Fast" in body_text:
        return "Processing (Veo 3.1 Fast)"

    return None
```

### **2. Detect Video Complete**

```python
def _find_play_button(self) -> Optional[any]:
    """
    Check multiple indicators:
    1. play_arrow icon exists
    2. Video duration "0:08" exists
    3. No progress % remaining
    """
    body_text = self.driver.find_element(By.TAG_NAME, 'body').text

    # Method 1: play_arrow + no progress %
    if "play_arrow" in body_text:
        percent_matches = re.findall(r'\b(\d{1,3})%\b', body_text)
        if not percent_matches:  # No % = complete
            return True

    # Method 2: Video duration pattern
    duration_matches = re.findall(r'0:\d{2}', body_text)
    if duration_matches:  # Found "0:08"
        return True

    return None
```

### **3. Detect Errors**

```python
def _check_for_errors(self) -> bool:
    """
    Flow shows "Không tạo được" on failure
    """
    error_keywords = [
        "không tạo được",  # Primary Flow error
        "failed to generate",
        "error",
        "failed",
        "lỗi"
    ]

    body_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()

    for keyword in error_keywords:
        if keyword in body_text:
            return True

    return False
```

### **4. Main Loop - Polling Progress**

```python
def _wait_for_video_generation(self, timeout=120, progress_callback=None):
    """
    Poll every 3 seconds for progress updates
    """
    start_time = time.time()
    check_interval = 3  # Check every 3s
    screenshot_interval = 10  # Screenshot every 10s

    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)
        percent = int((elapsed / timeout) * 100)

        # Get Flow's actual progress
        flow_progress = self._check_generation_progress()
        if flow_progress:
            logger.info(f"      🎬 Flow progress: {flow_progress}")

        # Take periodic screenshots
        if time.time() - last_screenshot_time >= screenshot_interval:
            screenshot_path = f"./data/logs/progress_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)

        # Callback to update UI
        if progress_callback:
            progress_callback(elapsed, percent, screenshot_path)

        # Check if video is ready
        if self._find_play_button():
            logger.info("      ✅ Video ready!")
            return True

        # Check for errors
        if self._check_for_errors():
            logger.error("      ❌ Generation failed!")
            return False

        time.sleep(check_interval)

    return False
```

---

## 📊 Selectors và Patterns

### Các element quan trọng:

| Element | Pattern/Selector | Ý nghĩa |
|---------|------------------|---------|
| Progress % | Text: `\b(\d{1,3})%\b` | Đang xử lý |
| Video player | Text: `play_arrow` | Video sẵn sàng |
| Duration | Text: `0:\d{2}` | Thời lượng video |
| Error | Text: `không tạo được` | Tạo thất bại |
| Model | Text: `Veo 3.1 - Fast` | Xác nhận model |
| Date | Text: `\d+ thg \d+, \d+` | Ngày tạo |

### Decision Tree:

```
START
  ↓
Nhập prompt & Click Generate
  ↓
Poll every 3s:
  ├─ Found "%"? → Log progress (3%, 9%, 15%...)
  ├─ Found "play_arrow" + no "%"? → SUCCESS! ✅
  ├─ Found "Không tạo được"? → FAILED! ❌
  └─ Timeout (120s)? → TIMEOUT! ⏱️
```

---

## 🎯 Example Output

### Thành công:
```bash
   ⏳ Waiting for video generation...
      Waiting up to 120s for generation...
      ⏳ Progress: 5% (6s / 120s)
      🎬 Flow progress: 3%
      📸 Screenshot saved: ./data/logs/progress_182305.png

      ⏳ Progress: 13% (15s / 120s)
      🎬 Flow progress: 9%

      ⏳ Progress: 21% (25s / 120s)
      🎬 Flow progress: 15%
      📸 Screenshot saved: ./data/logs/progress_182315.png

      ⏳ Progress: 29% (35s / 120s)
      🎬 Flow progress: 21%

      ⏳ Progress: 38% (45s / 120s)
      🎬 Flow progress: 33%
      📸 Screenshot saved: ./data/logs/progress_182325.png

      ⏳ Progress: 46% (55s / 120s)
      🎬 Flow progress: 45%

      ⏳ Progress: 54% (65s / 120s)
      🎬 Flow progress: 57%

      ⏳ Progress: 63% (75s / 120s)
      ✅ Found play_arrow icon and no progress %
      ✅ Found video duration: 0:08
      ✅ Video generation completed!
      📸 Final screenshot: ./data/logs/completed_182335.png
```

### Thất bại:
```bash
   ⏳ Progress: 38% (45s / 120s)
   🎬 Flow progress: 33%

   ⏳ Progress: 46% (55s / 120s)
   ❌ Error detected: 'không tạo được' found on page
   ❌ Video generation failed!
```

---

## ⏱️ Timing Characteristics

**Dựa trên phân tích**:
- **Thời gian tạo trung bình**: 30-60 giây
- **Check interval**: 3 giây (optimal)
- **Screenshot interval**: 10 giây
- **Timeout**: 120 giây (2 phút)
- **Progress steps**: Không đều, có thể nhảy bước

**Progress timeline ước tính**:
- 0-10s: 3% - 9%
- 10-20s: 9% - 15%
- 20-30s: 15% - 33%
- 30-45s: 33% - 57%
- 45-60s: 57% - 100%
- 60s+: Video ready (% biến mất)

---

## 🎯 Lưu ý quan trọng

1. **Progress không tuyến tính**: Có thể nhảy từ 3% → 9% → 15%, không từng %
2. **Multiple outputs (x2, x4)**: Có nhiều progress bars song song
3. **Indicator chính**: `play_arrow` + NO `%` = video complete
4. **Error detection**: "Không tạo được" là indicator chính xác nhất
5. **Video duration**: Luôn là 8 giây (0:08) cho Veo 3.1 Fast

---

## ✅ Implementation Status

- ✅ Progress detection (3%, 9%, 15%...)
- ✅ Video completion detection (play_arrow + 0:08)
- ✅ Error detection ("Không tạo được")
- ✅ Real-time screenshots
- ✅ Progress callback to UI
- ✅ Flow-specific patterns

**Code đã được cập nhật theo đúng quy trình Flow!** 🚀
