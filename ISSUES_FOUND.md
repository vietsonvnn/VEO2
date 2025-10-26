# 🐛 ISSUES FOUND - User Testing Session

## Test Date: 26/10/2025 - 19:06

User tested VEO 3.1 với topic "Hanoi Awakening" và phát hiện 3 issues quan trọng.

---

## ✅ Issue 1: 'int' object is not subscriptable [FIXED]

### Problem:
```python
TypeError: 'int' object is not subscriptable
```

Error xảy ra khi create videos, app crash tại line:
```python
for i, scene_data in enumerate(scenes_data):
```

### Root Cause:
`create_videos()` returns `Dict[int, Dict]` (dictionary với key là scene number)
Nhưng code đang dùng `enumerate()` như thể nó là list.

### Fix:
```python
# BEFORE (Wrong):
for i, scene_data in enumerate(scenes_data):
    scene = state.scenes[i]

# AFTER (Correct):
for scene_num, scene_data in scenes_data.items():
    scene = state.scenes[scene_num - 1]  # Convert to 0-indexed
```

### Status: ✅ FIXED
- Committed: f61dbba
- Pushed to: origin/main

---

## ⚠️ Issue 2: Aspect Ratio Button Không Hoạt Động [IN PROGRESS]

### Problem:
User chọn 16:9 (ngang) trong UI nhưng kết quả vẫn là 9:16 (dọc).

### Screenshot Evidence:
![Flow UI](user_screenshot_flow_ui_1.png)
- User chọn: 16:9
- Kết quả: Video vẫn dọc (9:16)

### Root Cause:
Selector không đúng:
```python
# Current (not working):
landscape_btn = await self.page.query_selector('button:has-text("crop_landscape")')
```

Flow UI không dùng text "crop_landscape" trong button, có thể dùng:
- Icon material: `crop_landscape`
- Radio buttons
- Hoặc label khác

### Proposed Fix:
```python
# Search through all elements for aspect ratio icon
all_elements = await self.page.query_selector_all('button, label, div, span')

target_icon = "crop_portrait" if aspect_ratio == "9:16" else "crop_landscape"
target_label = "9:16" if aspect_ratio == "9:16" else "16:9"

for elem in all_elements:
    inner_html = await elem.inner_html()
    inner_text = await elem.inner_text()

    # Check if element contains icon OR ratio text
    if target_icon in inner_html or target_label in inner_text:
        await elem.click()
        break
```

### Status: ⚠️ IN PROGRESS
- Need to test with Electron browser to verify selector
- May need screenshot/DOM inspection

---

## ❌ Issue 3: Videos Không Hiển Thị Trong UI [CRITICAL]

### Problem:
Videos được tạo thành công (có URL) nhưng KHÔNG hiển thị trong UI cards.

### Screenshot Evidence:
![UI Cards](user_screenshot_ui_1.png)
- Phần "Media đã tạo": Chỉ hiển thị "Chưa tạo"
- Không có video player
- URL tồn tại nhưng không render

### Root Cause Analysis:

#### Cause 1: Google Storage URLs Không Play Trực Tiếp
Google Storage URLs format:
```
https://storage.googleapis.com/ai-sandbox-videofx/video/{hash}
```

**Problem**:
- URLs này là private storage
- Không thể embed trực tiếp vào `<video src="...">`
- Cần authentication headers hoặc signed URLs

**Current Code:**
```python
video_html = f"""
<video controls>
    <source src="{scene['video_path']}" type="video/mp4">
</video>
"""
```

**Why It Fails:**
1. Browser tries to fetch `storage.googleapis.com/...`
2. Gets 403 Forbidden (no auth)
3. Video element shows "Unable to play"

#### Cause 2: Video Path Not Set Correctly
```python
scene['video_path'] = scene_data['video_url']
```

If `video_url` is None or empty, video won't show.

### Proposed Solutions:

#### Solution A: Use Gradio Video Component (Recommended)
```python
# In build_scenes_html(), instead of raw HTML:
if scene.get('video_path'):
    # Store video URL in state
    # Return Gradio Video component
    return gr.Video(value=scene['video_path'])
```

**Pros:**
- Gradio handles authentication
- Better player controls
- Mobile-friendly

**Cons:**
- Requires refactor of card layout
- May need to change from HTML to Components

#### Solution B: Download and Serve Locally
```python
async def download_video(video_url: str, scene_num: int) -> str:
    """Download video from Google Storage to local"""
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as resp:
            content = await resp.read()

    # Save to local
    local_path = f"./data/videos/scene_{scene_num}.mp4"
    with open(local_path, 'wb') as f:
        f.write(content)

    return local_path

# Then in build_scenes_html():
video_html = f"""
<video controls>
    <source src="/file={local_path}" type="video/mp4">
</video>
"""
```

**Pros:**
- Works with current HTML approach
- Videos cached locally
- Fast playback

**Cons:**
- Extra download time
- Storage space needed
- Need to handle Gradio file serving

#### Solution C: Open in New Tab
```python
# Fallback: Add button to open video in Flow
video_html = f"""
<div style="text-align: center; padding: 40px;">
    <p>✅ Video created successfully</p>
    <a href="{scene['video_path']}" target="_blank"
       style="display: inline-block; padding: 12px 24px;
              background: #3b82f6; color: white;
              text-decoration: none; border-radius: 6px;">
        🎬 Open Video in Flow
    </a>
</div>
"""
```

**Pros:**
- Simple, quick fix
- No download needed
- Works immediately

**Cons:**
- Not ideal UX
- User has to leave app
- Can't preview in-line

### Recommended Approach:
**Hybrid Solution:**
1. Try to show video in-line (Solution B - download)
2. If fails, show "Open in Flow" button (Solution C)
3. Add download progress indicator

```python
async def handle_video_display(scene, scene_data):
    video_url = scene_data['video_url']

    if not video_url:
        return "<p>❌ No video created</p>"

    try:
        # Try download
        local_path = await download_video(video_url, scene['number'])
        scene['video_path'] = local_path

        return f"""
        <video controls style="width: 100%;">
            <source src="/file={local_path}" type="video/mp4">
        </video>
        """
    except Exception as e:
        # Fallback: Open in new tab
        return f"""
        <div>
            <p>⚠️ Cannot display video inline</p>
            <a href="{video_url}" target="_blank">
                🎬 Open Video in Flow
            </a>
        </div>
        """
```

### Status: ❌ CRITICAL - NOT FIXED
- Requires implementation of video download/serving
- Need to test with Gradio file serving
- May need UI refactor

---

## 📊 Priority Summary

| Issue | Severity | Status | Effort |
|-------|----------|--------|--------|
| #1: Dict iteration | High | ✅ Fixed | Low |
| #2: Aspect ratio | Medium | ⚠️ In Progress | Medium |
| #3: Video display | **CRITICAL** | ❌ Not Fixed | High |

---

## 🎯 Next Steps

1. **Immediate**: Fix Issue #3 (video display) - CRITICAL for UX
2. **Soon**: Fix Issue #2 (aspect ratio selector)
3. **Test**: Full workflow with all fixes applied

---

## 📝 Notes

- Issue #1: Simple fix, already committed
- Issue #2: Need DOM inspection in Flow to find correct selector
- Issue #3: Most important, affects core functionality - user can't see videos!

User feedback shows videos ARE being created (progress 47% visible in Flow),
but UI doesn't show them. This is UX-breaking.

