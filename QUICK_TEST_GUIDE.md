# 🚀 QUICK TEST GUIDE - VEO 3.1

## TL;DR - Start App Ngay

```bash
./start_clean.sh
```

Hoặc:

```bash
cd /Users/macos/Desktop/VEO2
source venv312/bin/activate
python app.py
```

Mở browser: **http://localhost:7860**

---

## ✨ Features Mới Cần Test

### 1. **Instant Input** ⚡
- **Before**: Input chậm ~10s per prompt (typing với delay)
- **After**: Input <1s per prompt (fill instant)
- **Test**: Tạo video và xem log "Filling prompt..." - phải nhanh

### 2. **Aspect Ratio** 📐
- **Choices**: 16:9 (ngang) | 9:16 (dọc)
- **Default**: 16:9
- **Test**:
  - Chọn 16:9 → Video ngang (landscape)
  - Chọn 9:16 → Video dọc (TikTok/Reels)

### 3. **Model Selection** 🎨
- **Choices**: Veo 3.1 - Fast | Veo 3.1 - Quality
- **Default**: Veo 3.1 - Fast
- **Test**:
  - Fast = Nhanh hơn, quality tốt
  - Quality = Chậm hơn, quality cao hơn

---

## 📝 Test Workflow (5 phút)

### Step 1: Generate Script
1. **Topic**: "Làm bánh mì Việt Nam"
2. **Duration**: 1 phút
3. **Aspect Ratio**: Chọn 16:9 hoặc 9:16
4. **Model**: Chọn Fast hoặc Quality
5. Click **"📝 1. Tạo kịch bản"**

**Expected Output:**
```
✅ Hướng dẫn làm bánh mì Việt Nam
📝 [Description]
🎬 2 cảnh
📐 Tỷ lệ: 16:9
🎨 Model: Veo 3.1 - Fast
```

### Step 2: Create Videos
1. Click **"🎬 2. Tạo videos"**
2. Monitor log (expand "📊 Log chi tiết")
3. Verify:
   - ✅ Browser opens (Electron)
   - ✅ Settings applied (aspect ratio + model)
   - ✅ **Input instant** (<1s, không chậm)
   - ✅ Videos created
   - ✅ Videos displayed in cards

### Step 3: Test Regenerate (Optional)
1. Click **🔄 Tạo lại** on any card
2. New video should replace old one

### Step 4: Test Delete (Optional)
1. Click **🗑️ Xóa** on any card
2. Video deleted from Flow + UI

---

## ✅ Success Checklist

- [ ] App starts without errors
- [ ] UI có aspect ratio radio (16:9 / 9:16)
- [ ] UI có model dropdown (Fast / Quality)
- [ ] Script generation shows selected settings
- [ ] **Input instant** (~1s, không typing chậm)
- [ ] Settings applied (check log)
- [ ] Videos created successfully
- [ ] Videos match scenes (correct URLs)
- [ ] Regenerate works
- [ ] Delete works

---

## 🐛 Common Issues

### Port 7860 In Use
```bash
lsof -ti:7860 | xargs kill -9
```

### Cookies Expired
- Re-export cookies from Flow
- Save to `config/cookies.json`

### Browser Not Opening
```bash
playwright install chromium
```

---

## 📁 Files to Check

### Main Files:
- `app.py` - Gradio UI (updated with settings)
- `flow_video_tracker.py` - Core engine (instant fill + settings)
- `config/cookies.json` - Flow cookies
- `.env` - API key

### New Files:
- `TEST_ENVIRONMENT.md` - Full test documentation
- `start_clean.sh` - Clean startup script
- `Setting_Intro.txt` - Flow UI reference

---

## 🎯 Quick Commands

**Start app:**
```bash
./start_clean.sh
```

**Kill everything:**
```bash
pkill -9 python
lsof -ti:7860 | xargs kill -9
```

**Check status:**
```bash
# Check port
lsof -i:7860

# Check Python processes
ps aux | grep python
```

---

## 📊 Performance Comparison

| Feature | Before | After | Improvement |
|---------|--------|-------|-------------|
| Input Speed | ~10s | <1s | **10x faster** |
| Settings | Manual | Auto-applied | **Automated** |
| Aspect Ratio | Fixed | Configurable | **Flexible** |
| Model | Fixed | Selectable | **Choice** |

---

## 💡 Tips

1. **First Time**: May be slow due to browser download
2. **Cookies**: Re-export every 7 days
3. **Settings**: Applied before each video batch
4. **Logs**: Expand "📊 Log chi tiết" to see details
5. **Browser**: Don't close manually - let app handle it

---

Happy Testing! 🎉

Nếu có issues → Check [TEST_ENVIRONMENT.md](TEST_ENVIRONMENT.md) để troubleshooting chi tiết.
