# 🎬 Test Video Generation

## ✅ Đã Cài Đặt Xong

- [x] Python dependencies
- [x] Playwright
- [x] Chromium browser
- [x] Cookies configured

## 🚀 Test Ngay

### Bước 1: Test Browser (30 giây - KHÔNG tốn quota)

```bash
cd C:\Users\Trading\veo-automation
python test_browser_simple.py
```

**Sẽ thấy gì:**
- Browser Chromium mở ra
- Truy cập https://labs.google/fx/vi/tools/flow
- Kiểm tra đã đăng nhập chưa

**Nếu thấy Flow interface và đã logged in → OK!**

---

### Bước 2: Test Script → Video (Từ script có sẵn)

Bạn đã có script test từ lần trước:

```bash
# List scripts
dir data\scripts\*.json

# Example output:
# script_20251024_225450.json  (30s video, 3 scenes)
# script_20251024_230337.json  (24s video, 3 scenes)
```

**Generate video:**

```bash
python main.py --from-script data\scripts\script_20251024_230337.json
```

**Thời gian:** ~20-30 phút (3 scenes x 7 phút mỗi scene)

**Output:** `data\videos\project_xxx_final.mp4`

---

### Bước 3: Test Full Pipeline (Topic → Video)

```bash
# Tạo video ngắn 16s (2 scenes)
python main.py --topic "Sunset over ocean" --duration 16 --scene-duration 8

# Hoặc tiếng Việt
python main.py --topic "Hoàng hôn trên biển" --duration 16
```

---

## 📋 Commands Cheat Sheet

```bash
# Test browser only (no quota)
python test_browser_simple.py

# Generate script only (no quota)
python gen_script.py --topic "Your topic" --duration 30

# Generate video from existing script
python main.py --from-script data\scripts\script_xxx.json

# Full automation (topic → script → videos → merge)
python main.py --topic "Your topic" --duration 30

# Web UI
python app.py
# or
.\run_ui.bat
```

---

## ⚠️ Troubleshooting

### Browser shows "Not logged in"

**Fix:** Extract new cookies

1. Open Chrome/Edge normally
2. Go to https://labs.google/fx/vi/tools/flow
3. Login with Google account
4. Install Cookie Editor extension
5. Export cookies as JSON
6. Save to `cookies_raw.json`
7. Run:
   ```bash
   python tools\extract_cookies.py cookies_raw.json
   ```

### Video generation timeout

- VEO might be overloaded
- Try again later
- Increase timeout in config.yaml

### DOM selectors not found

Flow UI might have changed. Update selectors in:
`src\browser_automation\flow_controller.py`

---

## 💡 Recommendations

### First Time Testing:

1. ✅ **Test browser access first**
   ```bash
   python test_browser_simple.py
   ```

2. ✅ **Generate a short video (16s)**
   ```bash
   python main.py --topic "Test video" --duration 16
   ```

3. ✅ **If successful, try longer videos**

### Best Practices:

- Start with 16-30s videos (2-4 scenes)
- Review scripts before generating
- Monitor your VEO quota
- Keep cookies fresh (re-extract every 2 weeks)

---

## 📊 Expected Results

### For 16s video (2 scenes):
- Script generation: 10-30s
- Video generation: 10-15 minutes
- Download: 1-2 minutes
- Merge: 30s
- **Total: ~15-20 minutes**

### For 30s video (3-4 scenes):
- **Total: ~25-35 minutes**

### For 60s video (8 scenes):
- **Total: ~50-70 minutes**

---

## 🎯 Next Step

**Start with simple browser test:**

```bash
python test_browser_simple.py
```

Nếu thành công, bạn sẵn sàng generate videos! 🚀
