# Electron Video Tracker - Thử nghiệm

## Vấn đề hiện tại với Selenium

1. **Video mapping không chính xác**
   - Flow tạo 2 videos mỗi prompt (x2 mode)
   - Khó track chính xác video nào thuộc scene nào
   - Phải dựa vào "first new URL" - không 100% reliable

2. **Performance**
   - Selenium có overhead lớn
   - WebDriver protocol chậm hơn
   - Khó monitor real-time network events

## Ưu điểm của Electron với Playwright

### 1. **Network Monitoring chính xác hơn**
```python
# Playwright có thể intercept network requests
page.on("response", lambda response:
    if "storage.googleapis.com" in response.url:
        video_urls.append(response.url)
)
```

### 2. **Async/Await native**
- Code cleaner và dễ maintain
- Better concurrent operations
- Real-time event handling

### 3. **DevTools Protocol trực tiếp**
- Access Chrome DevTools Protocol
- Monitor network, console, performance
- Better debugging capabilities

### 4. **Video Mapping Strategy**

```python
class ElectronVideoTracker:
    def __init__(self):
        self.video_map = {}  # scene_number -> video_url

    async def track_video_creation(self, scene_number, prompt):
        # 1. Baseline: Get current URLs
        urls_before = await self._get_all_video_urls()

        # 2. Fill prompt and generate
        await self._fill_prompt(prompt)
        await self._click_generate()

        # 3. Wait for NEW video URL
        new_url = await self._wait_for_new_video(urls_before)

        # 4. Map to scene
        self.video_map[scene_number] = new_url

        return new_url
```

## So sánh Performance

| Feature | Selenium | Playwright/Electron |
|---------|----------|---------------------|
| Startup time | ~5s | ~2s |
| Network monitoring | ❌ Limited | ✅ Full |
| Async support | ❌ Sync only | ✅ Native async |
| DevTools access | ⚠️ Limited | ✅ Full |
| Real-time events | ❌ Polling only | ✅ Event-driven |

## Kế hoạch Test

### Phase 1: Prototype (DONE ✅)
- [x] Tạo ElectronVideoTracker class
- [x] Implement basic tracking logic
- [x] Test với 3 scenes

### Phase 2: Integration
- [ ] Tích hợp vào app.py
- [ ] So sánh accuracy với Selenium
- [ ] Measure performance

### Phase 3: Production
- [ ] Replace Selenium hoàn toàn
- [ ] Add error handling
- [ ] Optimize for batch operations

## Cách chạy test

```bash
# Test Electron tracker
source venv312/bin/activate
python electron_video_tracker.py
```

## Expected Output

```
🚀 Starting Electron browser...
✅ Electron browser started
📁 Going to project: 7527ed36-b1fb-4728-9cac-e42fc01698c4
✅ Project loaded

============================================================
🎬 SCENE 1: A serene morning landscape with mountains and fog
============================================================
📊 Baseline: 0 videos on page
✍️  Filling prompt...
🎯 Clicking Generate...
👀 Monitoring for new video...
   ⏳ Waiting... 3s / 120s
   ⏳ Waiting... 6s / 120s
   ...
   ✅ Play button found!
   📹 Found 1 new video(s)
✅ Scene 1 → https://storage.googleapis.com/ai-sandbox-videofx/video/abc123...

============================================================
📊 FINAL VIDEO MAPPING:
============================================================
Scene 1: https://storage.googleapis.com/ai-sandbox-videofx/video/abc123...
Scene 2: https://storage.googleapis.com/ai-sandbox-videofx/video/def456...
Scene 3: https://storage.googleapis.com/ai-sandbox-videofx/video/ghi789...
```

## Kết luận

Electron/Playwright approach cho phép:
- ✅ **Chính xác hơn** trong việc map video → scene
- ✅ **Nhanh hơn** với async operations
- ✅ **Dễ maintain** với modern async/await syntax
- ✅ **Better debugging** với DevTools Protocol

Sau khi test thành công, có thể replace Selenium hoàn toàn!
