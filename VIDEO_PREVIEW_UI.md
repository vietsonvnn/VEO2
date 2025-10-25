# 🎬 Video Preview & Regenerate UI

## 📋 Overview

Enhanced Gradio UI cho phép user xem preview video và regenerate từng video riêng biệt nếu chưa ưng ý.

## ✨ Features

### 1. **Video Preview Grid**
- Hiển thị tối đa 10 scenes cùng lúc
- Mỗi scene có:
  - 🎥 Video player để xem preview
  - 📊 Status indicator (⏳ Pending, 🎬 Generating, ✅ Completed, ❌ Failed)
  - 🔄 Regenerate button để tạo lại video
  - ℹ️ Info button để xem chi tiết prompt

### 2. **Individual Video Regeneration**
- Click button "🔄 Regenerate Scene X" để tạo lại video specific
- Video mới sẽ thay thế video cũ
- Không ảnh hưởng đến các scenes khác

### 3. **Real-time Status Tracking**
- **⏳ Pending**: Chưa bắt đầu generate
- **🎬 Generating**: Đang tạo video (5-7 phút)
- **✅ Completed**: Hoàn thành và ready to preview
- **❌ Failed**: Lỗi (xem error detail bằng Info button)

### 4. **Batch Generation**
- Button "🚀 Generate All Videos" để tạo tất cả scenes
- Tự động queue và generate tuần tự
- Progress tracking cho từng scene

## 🚀 Usage

### Step 1: Load Script
```
1. Select script từ dropdown "📄 Saved Scripts"
2. Click "📂 Load Script"
3. Xem thông tin script và danh sách scenes
```

### Step 2: Generate Videos
```
Option A - Generate All:
1. Click "🚀 Generate All Videos"
2. Đợi tất cả scenes được generate (30-60 phút cho 8 scenes)

Option B - Generate Individual:
1. Click "🔄 Regenerate Scene X" cho scene cụ thể
2. Đợi scene đó hoàn thành (5-7 phút)
```

### Step 3: Preview & Review
```
1. Video player sẽ tự động load khi scene completed
2. Click play để xem preview
3. Nếu không ưng ý → Click "🔄 Regenerate" để tạo lại
4. Click "ℹ️ Info" để xem prompt và error (nếu có)
```

## 🎯 Workflow Example

```
1. Load script "Amazon_Rainforest.json"
   → Shows 8 scenes in grid

2. Click "🚀 Generate All Videos"
   → Scene 1: ⏳ → 🎬 → ✅
   → Scene 2: ⏳ → 🎬 → ✅
   → Scene 3: ⏳ → 🎬 → ❌ (Failed)
   → ...

3. Preview Scene 3 error
   → Click "ℹ️ Info" → See error: "Generation timeout"

4. Regenerate Scene 3
   → Click "🔄 Regenerate Scene 3"
   → Status: 🎬 → ✅
   → New video replaces old one

5. Review all videos
   → All scenes ✅
   → Ready to merge or export
```

## 🖥️ UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 VEO 3.1 Video Automation - Enhanced                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌────────────────────────────────────┐  │
│  │ 1. Script    │  │  3. Video Preview Grid              │  │
│  │              │  │                                      │  │
│  │ [Dropdown]   │  │  ┌──────────┬────────┬─────────┐   │  │
│  │              │  │  │ Scene 1  │Status: │[Regen]  │   │  │
│  │ [Load]       │  │  │ [Video]  │   ✅   │[Info]   │   │  │
│  │              │  │  ├──────────┼────────┼─────────┤   │  │
│  │ Script Info  │  │  │ Scene 2  │Status: │[Regen]  │   │  │
│  │ - Title      │  │  │ [Video]  │   🎬   │[Info]   │   │  │
│  │ - Scenes: 8  │  │  ├──────────┼────────┼─────────┤   │  │
│  │ - Duration   │  │  │ Scene 3  │Status: │[Regen]  │   │  │
│  │              │  │  │ [Empty]  │   ⏳   │[Info]   │   │  │
│  │              │  │  └──────────┴────────┴─────────┘   │  │
│  │ 2. Generate  │  │                                      │  │
│  │              │  │  ... (more scenes)                   │  │
│  │ [🚀 Start]   │  │                                      │  │
│  │              │  │                                      │  │
│  │ Status Log   │  │                                      │  │
│  └──────────────┘  └────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Key Implementation Details

### Video State Management
```python
current_project_state = {
    "script": {...},              # Loaded script
    "project_id": "abc123",       # Flow project ID
    "videos": [                   # Video status for each scene
        {
            "scene_index": 0,
            "scene_number": 1,
            "prompt": "...",
            "description": "...",
            "status": "completed",
            "download_path": "./data/videos/scene_001.mp4",
            "error": None
        },
        ...
    ]
}
```

### Regenerate Logic
```python
async def regenerate_video(scene_index):
    # 1. Update status to "generating"
    video_data["status"] = "generating"

    # 2. Create new video with same prompt
    await controller.create_video_from_prompt(prompt)

    # 3. Wait for completion
    await controller.wait_for_video_completion()

    # 4. Download new video (overwrites old one)
    download_path = await controller.download_video_from_ui()

    # 5. Update status to "completed"
    video_data["status"] = "completed"
    video_data["download_path"] = download_path
```

## 🔧 Technical Stack

- **Frontend**: Gradio (video player, buttons, status displays)
- **Backend**: Async Python (asyncio for video generation)
- **Browser Automation**: Playwright (Flow controller)
- **State Management**: Global dict for video tracking

## ⚠️ Important Notes

### Performance
- **Batch generation**: ~5-7 minutes per scene
- **8 scenes**: 40-60 minutes total
- **Regenerate**: 5-7 minutes per video

### Limitations
- Maximum 10 scenes per script (UI grid limitation)
- Videos generated sequentially (not parallel)
- Requires valid Flow cookies
- VEO 3.1 quota needed

### Best Practices

1. **Start small**: Test with 2-3 scenes first
2. **Monitor status**: Check status log regularly
3. **Save cookies**: Refresh cookies if expired
4. **Check quota**: Ensure VEO 3.1 quota available
5. **Regenerate sparingly**: Each regeneration uses quota

## 📝 Example Session

```bash
# 1. Start the enhanced UI
python app_with_preview.py

# 2. Access at http://localhost:7861

# 3. Workflow:
- Load script: "data/scripts/script_20250125_123456.json"
- Generate all: Click "🚀 Generate All Videos"
- Wait: 40-60 minutes for 8 scenes
- Review: Check each video preview
- Regenerate: Scene 3, 5 if needed
- Export: All videos ready in ./data/videos/
```

## 🎯 Future Enhancements

- [ ] Parallel generation (multiple scenes at once)
- [ ] Custom prompt editing before regeneration
- [ ] Video quality comparison (old vs new)
- [ ] Export merged video directly from UI
- [ ] Progress bar for each scene generation
- [ ] Notification when generation completes
- [ ] Cloud storage integration
- [ ] Collaborative review (multi-user)

---

**Made with ❤️ for VEO 3.1 Automation**
