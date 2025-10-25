# ⚡ Quick Reference - VEO 3.1 Movie Production

## 🚀 Start
```bash
source venv312/bin/activate && python app.py
# http://localhost:7860
```

## 📋 Required Inputs

| Field | Value | Example |
|-------|-------|---------|
| **Chủ đề** | Topic của phim | "Hướng dẫn nấu phở" |
| **Thời lượng** | 0.5 - 3 phút | 1 phút → 7 scenes |
| **Cookies** | Path to cookie file | `./cookie.txt` |
| **Project ID** | Flow project ID | `abc123def456` ⭐ |

⭐ **QUAN TRỌNG**: Luôn nhập Project ID từ Flow!

## 🔑 Lấy Project ID

1. Vào https://labs.google/fx/vi/tools/flow
2. Tạo project mới (hoặc dùng cũ)
3. Copy từ URL:
   ```
   https://labs.google/fx/vi/tools/flow/project/abc123def456
                                                ^^^^^^^^^^^^
   ```

## 🎬 3 Steps

### Step 1: Tạo kịch bản
```
Input topic + duration → Click "Tạo kịch bản"
→ Gemini AI tạo N scenes × 8s
```

### Step 2: Tạo videos
```
Click "Tạo tất cả video"
→ Browser mở → Vào Flow → Vào Project → Tạo từng scene
→ Download tất cả về ./data/projects/.../videos/
```

### Step 3: Ghép phim
```
Tab "Video cuối" → Click "Nối video"
→ final.mp4 (tất cả scenes ghép lại)
```

## 🔄 Regenerate Scene

Tab "Xem & tạo lại" → Click "Tạo lại Scene X"
→ VEO tạo lại scene đó với cùng prompt

## 📂 Output

```
./data/projects/YYYYMMDD_HHMMSS/
├── videos/
│   ├── scene_001.mp4 (8s)
│   ├── scene_002.mp4 (8s)
│   └── ...
└── final.mp4 (N×8s)
```

## ⚠️ Common Errors

| Error | Fix |
|-------|-----|
| "Không thể tạo project" | ✅ Nhập Project ID có sẵn |
| "Không thể vào project" | Kiểm tra Project ID, cookies |
| "Tất cả cảnh thất bại" | Update cookies, nhập Project ID |

## 💡 Pro Tips

✅ **DOs**
- Luôn dùng Project ID có sẵn
- Kiểm tra cookies còn hạn
- Xem browser tự động hoạt động
- Regenerate scenes không đẹp

❌ **DON'Ts**
- Để trống Project ID (có thể fail)
- Dùng cookies cũ/hết hạn
- Tạo quá nhiều scenes (>20 mất thời gian)

## 📊 Duration Guide

| Minutes | Scenes | Time |
|---------|--------|------|
| 0.5 | 3-4 | ~5 min |
| 1.0 | 7-8 | ~10 min |
| 1.5 | 11-12 | ~15 min |
| 2.0 | 15 | ~20 min |
| 3.0 | 22-23 | ~30 min |

## 🎯 Example Workflow

```
1. Nhập Project ID: abc123def456     ⭐
2. Topic: "Pha cà phê Việt Nam"
3. Duration: 1 phút
4. "Tạo kịch bản" → 7 scenes
5. "Tạo tất cả video" → 10-15 phút
6. Xem tab 2 → Regenerate scene 3, 5
7. Tab 3 → "Nối video" → final.mp4
8. Done! 🎉
```

## 🆘 Emergency

**Tất cả đều fail?**

1. ✅ Nhập Project ID
2. ✅ Update cookies (`cookie.txt`)
3. ✅ Kiểm tra đã đăng nhập Google
4. ✅ Restart: `Ctrl+C` → `python app.py`

---

**Remember**: Project ID is KEY! 🔑
