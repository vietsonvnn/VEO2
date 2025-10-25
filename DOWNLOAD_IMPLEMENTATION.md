# VEO 3.1 Download Implementation

## Overview

Successfully implemented video download functionality for the VEO 3.1 Video Automation System.

## Implementation Details

### Key Features

1. **Video Completion Detection** - [flow_controller.py:304-366](src/browser_automation/flow_controller.py#L304-L366)
   - Waits for video generation to complete by detecting play button
   - Progress logging every 30 seconds
   - Default 7-minute timeout (420 seconds)
   - Detects errors during generation

2. **Multi-Quality Download** - [flow_controller.py:384-564](src/browser_automation/flow_controller.py#L384-L564)
   - Supports 3 quality options:
     - **GIF (270p)**: `quality="gif"` or `quality="270p"`
     - **720p Original**: `quality="720p"`
     - **1080p Upscaled**: `quality="1080p"` (DEFAULT)
   - UI-based download (clicks buttons instead of direct URL download)
   - Fallback detection for files downloaded to default browser location

### Download Workflow

```python
# Based on Button2.txt and downloadvideo_1.txt
# Step 1: Click more options button (more_vert icon)
# Step 2: Click "Tải xuống" (Download) menu item
# Step 3: Select quality option from popup:
#         - "Ảnh GIF động (270p)"
#         - "Kích thước gốc (720p)"
#         - "Đã tăng độ phân giải (1080p)"
# Step 4: Handle download with Playwright or fallback to file detection
```

## Usage Examples

### Example 1: Download Existing Video

```python
from src.browser_automation import FlowController

controller = FlowController(
    cookies_path="./config/cookies.json",
    download_dir="./data/videos",
    headless=False
)

await controller.start()
await controller.goto_flow()
await controller.goto_project("PROJECT_ID")

# Download in 1080p (default)
download_path = await controller.download_video_from_ui(
    filename="my_video.mp4",
    prompt_text="cherry",  # Find video by prompt text
    quality="1080p"
)

# Download in 720p
download_path = await controller.download_video_from_ui(
    filename="my_video_720p.mp4",
    prompt_text="cherry",
    quality="720p"
)

# Download as GIF
download_path = await controller.download_video_from_ui(
    filename="my_video.gif",
    prompt_text="cherry",
    quality="gif"
)
```

### Example 2: Complete Workflow (Generate + Download)

```python
# Create video
await controller.goto_project("PROJECT_ID")

prompt = "A serene Japanese garden with cherry blossoms"
await controller.create_video_from_prompt(
    prompt=prompt,
    wait_for_generation=False
)

# Wait for completion
completed = await controller.wait_for_video_completion(timeout=420)

if completed:
    # Download the video
    download_path = await controller.download_video_from_ui(
        filename="cherry_blossom.mp4",
        prompt_text="cherry",
        quality="1080p"
    )
```

## Test Scripts

### 1. test_download_existing.py
Tests download functionality on already-generated videos.

```bash
python test_download_existing.py
```

Features:
- Navigates to existing project
- Finds video by prompt text ("cherry")
- Downloads in 1080p quality
- Browser stays visible for debugging

### 2. test_complete_workflow.py
Full end-to-end test including generation and download.

```bash
python test_complete_workflow.py
```

Features:
- Creates new video from prompt
- Waits for generation (5-7 minutes)
- Automatically downloads upon completion
- Comprehensive logging

### 3. inspect_download_ui.py
Diagnostic tool for inspecting download UI elements.

```bash
python inspect_download_ui.py
```

Features:
- Manual inspection mode
- Saves HTML and screenshots
- Helps debug selector issues

## Quality Options

| Quality | Button Text | Resolution | Format | Use Case |
|---------|-------------|------------|--------|----------|
| `"gif"` or `"270p"` | Ảnh GIF động (270p) | 270p | GIF | Animated preview, small file size |
| `"720p"` | Kích thước gốc (720p) | 720p | MP4 | Original quality |
| `"1080p"` | Đã tăng độ phân giải (1080p) | 1080p | MP4 | Best quality (upscaled) |

## Selectors Reference

### More Options Button
```python
selectors = [
    'button:has-text("more_vert")',
    'button[aria-label*="More"]',
    'button[aria-label*="options"]',
    '[role="button"]:has-text("more_vert")'
]
```

### Download Menu Item
```python
selectors = [
    'button:has-text("Tải xuống")',
    '[role="menuitem"]:has-text("Tải xuống")',
    'div:has-text("Tải xuống")',
    'button:has-text("Download")',
    '[role="menuitem"]:has-text("Download")'
]
```

### Quality Options
```python
quality_selectors = {
    "gif": 'button:has-text("Ảnh GIF động (270p)")',
    "270p": 'button:has-text("Ảnh GIF động (270p)")',
    "720p": 'button:has-text("Kích thước gốc (720p)")',
    "1080p": 'button:has-text("Đã tăng độ phân giải (1080p)")'
}
```

## Error Handling

The download method includes multiple fallbacks:

1. **Playwright Download Event**: Primary method using `expect_download()`
2. **File Detection Fallback**: If Playwright event fails, scans download directory for recent files
3. **Multiple Format Support**: Checks for .mp4, .webm, and .gif files
4. **Automatic Renaming**: Preserves original file extension if different from requested

## Known Issues & Limitations

1. **Download Event Detection**: Flow may use client-side blob downloads which don't always trigger Playwright's download event
2. **Video Card Selection**: Currently searches all `<div>` elements for prompt text - may be slow on pages with many elements
3. **Menu Timing**: Fixed 1-1.5 second delays after clicking menus - may need adjustment for slower connections

## Future Improvements

1. **Optimize Video Card Detection**: Use more specific selectors instead of searching all divs
2. **Direct Video URL Extraction**: Find and extract video URLs directly from DOM instead of UI automation
3. **Progress Tracking**: Monitor download progress for large files
4. **Batch Downloads**: Support downloading multiple videos in one operation
5. **Custom Download Location**: Allow specifying download path per video

## Dependencies

- Playwright >= 1.48.0
- Python >= 3.8
- Valid Flow cookies in `config/cookies.json`
- Active Google Labs Flow project

## References

- [Button2.txt](Button2.txt) - Post-generation UI controls
- [downloadvideo_1.txt](downloadvideo_1.txt) - Quality options documentation
- [SESSION_SUMMARY.md](SESSION_SUMMARY.md) - Complete session history

---

**Status**: ✅ Implementation complete, testing in progress
**Last Updated**: 2025-10-25
**Author**: VEO 3.1 Automation Team
