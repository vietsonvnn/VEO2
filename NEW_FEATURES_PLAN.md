# 🎯 New Features Implementation Plan

## Các tính năng mới cần implement:

### 1. ✅ **Flow Queue Limit Handling**
**Status**: DONE
- Flow giới hạn max 5 videos pending cùng lúc
- Check queue trước khi submit video mới
- Wait nếu queue đầy (5/5)

### 2. 🔄 **Video Gallery - Hiển thị TẤT CẢ scenes**
**Status**: IN PROGRESS
- Gallery component với tất cả videos
- Layout responsive cho nhiều scenes (3 columns)
- Click để xem từng video chi tiết
- Scalable cho 20-30+ scenes

### 3. 🎬 **Video Player cho scene đã chọn**
**Status**: IN PROGRESS
- Video player lớn khi click vào gallery
- Controls: play/pause/download
- Info: Scene number, description, status

### 4. 🔄 **Regenerate Button cho từng scene** ⭐ NEW
**Status**: TODO
- Button "Tạo lại" cho mỗi scene
- Re-submit prompt với cùng nội dung
- Replace video cũ bằng video mới
- History tracking (optional)

### 5. 📊 **Detailed Logging System** ⭐ NEW
**Status**: TODO
- Real-time log hiển thị đầy đủ
- Step-by-step progress
- Timestamp cho mỗi action
- Error details
- Queue status updates

---

## UI Layout đề xuất:

```
Tab "Tạo Video (Comet)":
┌─────────────────────────────────┬─────────────────────────────────┐
│ 📋 LOG REAL-TIME                │ 📸 Màn hình hiện tại (Comet)   │
│                                 │                                 │
│ [12:34:56] 🚀 Khởi động Comet  │  [Live Screenshot - 10s]        │
│ [12:34:58] ✅ Browser mở        │                                 │
│ [12:35:01] 📊 Queue: 2/5        │                                 │
│ [12:35:03] 🎬 Scene 1/7         │                                 │
│ [12:35:05]    Checking queue... │                                 │
│ [12:35:06]    ✅ Space available│                                 │
│ [12:35:08]    Nhập prompt...    │                                 │
│ [12:35:10]    Click Generate... │                                 │
│ [12:35:45]    Progress: 45%     │                                 │
│ [12:36:15]    ✅ Video xong!     │                                 │
│ [12:36:18]    📥 Downloaded     │                                 │
│ [12:36:20] ✨ Scene 1 DONE      │                                 │
└─────────────────────────────────┴─────────────────────────────────┘

🎬 Video Gallery - Tất cả cảnh đã tạo:
┌───────────────┬───────────────┬───────────────┐
│ Scene 1 ✅    │ Scene 2 ✅    │ Scene 3 ⏳    │
│ [Thumbnail]   │ [Thumbnail]   │ [Loading...]  │
│ "Kitchen..."  │ "Pot boil..." │ "Add spice...│
│ 🔄 Tạo lại    │ 🔄 Tạo lại    │   Đang tạo... │
├───────────────┼───────────────┼───────────────┤
│ Scene 4 ⏳    │ Scene 5 ⏳    │ Scene 6 ⏳    │
│ [Pending]     │ [Pending]     │ [Pending]     │
│ "Season..."   │ "Plate up..." │ "Serve..."    │
│   Chờ tạo...  │   Chờ tạo...  │   Chờ tạo...  │
└───────────────┴───────────────┴───────────────┘

🎬 Video đã chọn: Scene 1
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                    [VIDEO PLAYER]                            │
│                                                              │
│  ▶️  ══════════════════●────────  0:05 / 0:08               │
│                                                              │
│  Scene 1: Opening shot of traditional Vietnamese kitchen    │
│  Status: ✅ Completed                                        │
│  [Download] [Fullscreen] [🔄 Tạo lại scene này]             │
└──────────────────────────────────────────────────────────────┘

📊 Chi tiết trạng thái các cảnh: [Expandable JSON]
```

---

## Implementation Details:

### Feature 2 & 3: Video Gallery

**Code Structure**:
```python
# Track all videos
all_videos = []  # List of {"path": ..., "scene": ..., "status": ...}

# After each video completes
video_data = {
    "path": video_path,
    "scene_number": scene_num,
    "description": scene_desc,
    "status": "completed",
    "thumbnail": generate_thumbnail(video_path)  # Optional
}
all_videos.append(video_data)

# Return for gallery
return (logs, scene_status, screenshot, all_videos, selected_video)
```

**UI Components**:
```python
# Gallery for all videos
video_gallery = gr.Gallery(
    label="Videos",
    columns=3,  # 3 videos per row
    height="auto"
)

# Selected video player
selected_video = gr.Video(
    label="Scene đã chọn",
    height=500
)

# Event: Click gallery → Update player
video_gallery.select(
    fn=lambda evt: load_video(evt.index),
    outputs=[selected_video]
)
```

### Feature 4: Regenerate Button

**UI per Scene**:
```python
with gr.Row():
    for scene in state.scenes:
        with gr.Column():
            gr.Video(scene['path'])
            gr.Text(f"Scene {scene['number']}")
            regenerate_btn = gr.Button("🔄 Tạo lại")

            regenerate_btn.click(
                fn=regenerate_scene,
                inputs=[scene['number'], scene['prompt']],
                outputs=[video_gallery, logs]
            )
```

**Regenerate Function**:
```python
def regenerate_scene(scene_number, prompt):
    """
    Regenerate a specific scene
    """
    logger.info(f"🔄 Regenerating scene {scene_number}...")

    # Find scene
    scene = state.scenes[scene_number - 1]

    # Mark as regenerating
    scene['status'] = 'regenerating'

    # Call create_video with same prompt
    url = controller.create_video_from_prompt(
        prompt=scene['prompt'],
        aspect_ratio="16:9"
    )

    # Update scene
    if url:
        scene['url'] = url
        scene['video_path'] = url
        scene['status'] = 'completed'
        scene['regenerated'] = True  # Flag
    else:
        scene['status'] = 'failed'

    return update_gallery(), update_logs()
```

### Feature 5: Detailed Logging

**Logging System**:
```python
import logging
from datetime import datetime

class DetailedLogger:
    def __init__(self):
        self.logs = []

    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        log_line = f"[{timestamp}] {icon.get(level, '')} {message}"
        self.logs.append(log_line)
        print(log_line)  # Also print to console

    def info(self, msg):
        self.log("INFO", msg)

    def success(self, msg):
        self.log("SUCCESS", msg)

    def error(self, msg):
        self.log("ERROR", msg)

    def get_logs(self):
        return "\n".join(self.logs)

# Usage
detailed_logger = DetailedLogger()

detailed_logger.info("🚀 Khởi động Comet browser")
detailed_logger.info("📊 Checking Flow queue...")
detailed_logger.info("   Queue status: 2/5 pending")
detailed_logger.success("   ✅ Queue has space")
detailed_logger.info("🎬 Scene 1/7")
detailed_logger.info("   📝 Filling prompt...")
detailed_logger.success("   ✅ Prompt filled")
detailed_logger.info("   🎬 Clicking Generate...")
detailed_logger.info("   ⏳ Progress: 15% (18s)")
detailed_logger.info("   ⏳ Progress: 33% (40s)")
detailed_logger.success("   ✅ Video completed!")
```

**UI Display**:
```python
logs_output = gr.Textbox(
    label="📋 Detailed Logs",
    lines=30,
    max_lines=50,
    value=detailed_logger.get_logs(),
    every=1  # Auto-refresh every 1s
)
```

---

## Priority Order:

1. **✅ Queue Limit** - DONE
2. **🔄 Video Gallery** - IN PROGRESS (80%)
3. **📊 Detailed Logging** - HIGH PRIORITY
4. **🔄 Regenerate Button** - MEDIUM PRIORITY
5. **🎨 UI Polish** - LOW PRIORITY

---

## Testing Scenarios:

### Scenario 1: Small Project (3 scenes)
- Should fit nicely in 3-column gallery
- All videos visible without scrolling
- Fast generation

### Scenario 2: Medium Project (7-10 scenes)
- Gallery shows 3 columns, 3+ rows
- Scrollable gallery
- Queue management active (5 at a time)

### Scenario 3: Large Project (20+ scenes)
- Gallery becomes long (scrollable)
- Heavy queue management
- May take 10-15 minutes total
- Need progress indicators

### Scenario 4: Regenerate
- Click "Tạo lại" on scene 3
- Queue check (wait if full)
- Generate new video
- Replace old video in gallery
- Update status

---

## Next Steps:

1. Finish video gallery implementation
2. Add detailed logging system
3. Implement regenerate functionality
4. Test with various scene counts
5. Polish UI/UX
6. Documentation

