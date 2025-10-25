# 🍪 Hướng dẫn Export Cookies từ Browser

## ⚠️ VẤN ĐỀ HIỆN TẠI

Tool không thể login vào Flow vì **chưa có cookies**.

```
❌ Cookies file not found: ./cookie.txt
❌ Browser mở nhưng chưa đăng nhập
❌ Không thể tạo/vào project
```

---

## ✅ GIẢI PHÁP: Export cookies từ Chrome

### **Bước 1: Cài Extension "Get cookies.txt LOCALLY"**

1. Mở Chrome Web Store
2. Tìm: **"Get cookies.txt LOCALLY"**
3. Click **"Add to Chrome"**
4. Link: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

### **Bước 2: Đăng nhập Flow**

1. Mở: https://labs.google/fx/vi/tools/flow
2. Đăng nhập bằng Google account của bạn
3. Đảm bảo đã vào được Flow dashboard

### **Bước 3: Export cookies**

1. Click vào **icon Extension** (puzzle piece) trên thanh toolbar
2. Click **"Get cookies.txt LOCALLY"**
3. Click **"Export"**
4. File `cookies.txt` sẽ được download

### **Bước 4: Di chuyển file vào project**

```bash
# Di chuyển file cookies.txt vào thư mục VEO2
mv ~/Downloads/cookies.txt /Users/macos/Desktop/VEO2/cookie.txt

# Hoặc dùng Finder:
# - Mở Downloads folder
# - Kéo cookies.txt vào /Users/macos/Desktop/VEO2/
# - Đổi tên thành: cookie.txt (bỏ s)
```

### **Bước 5: Kiểm tra file**

```bash
cd /Users/macos/Desktop/VEO2
ls -la cookie.txt
# Nên thấy: -rw-r--r--  1 macos  staff  XXXXX ...  cookie.txt
```

---

## 🔄 CÁCH KHÁC: Export JSON format

Nếu extension trên không work, dùng cách này:

### **Option 1: EditThisCookie Extension**

1. Cài extension: https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
2. Vào https://labs.google/fx/vi/tools/flow
3. Click icon EditThisCookie
4. Click **Export** (icon xuất file)
5. Copy JSON
6. Tạo file `cookie.txt`:

```bash
cd /Users/macos/Desktop/VEO2
cat > cookie.txt << 'EOF'
[
  {
    "domain": ".google.com",
    "name": "SID",
    "value": "...",
    ...
  }
]
EOF
```

### **Option 2: Chrome DevTools**

1. Vào https://labs.google/fx/vi/tools/flow
2. Press `F12` (mở DevTools)
3. Vào tab **"Application"**
4. Bên trái click **"Cookies"** → **"https://labs.google"**
5. Copy từng cookie quan trọng:
   - `SID`
   - `HSID`
   - `SSID`
   - `APISID`
   - `SAPISID`

**Tạo file JSON:**

```json
[
  {
    "name": "SID",
    "value": "...",
    "domain": ".google.com",
    "path": "/",
    "expires": -1,
    "httpOnly": false,
    "secure": false,
    "sameSite": "Lax"
  },
  {
    "name": "HSID",
    "value": "...",
    "domain": ".google.com",
    "path": "/",
    "expires": -1,
    "httpOnly": true,
    "secure": false,
    "sameSite": "Lax"
  }
]
```

---

## 📝 Format cookies.txt (Netscape)

Nếu dùng extension "Get cookies.txt LOCALLY", file sẽ có format:

```
# Netscape HTTP Cookie File
.google.com	TRUE	/	FALSE	1234567890	SID	AJi4W2...
.google.com	TRUE	/	TRUE	1234567890	HSID	ARTBx3...
.google.com	TRUE	/	FALSE	1234567890	SSID	Apw3f5...
```

**Tool sẽ tự động convert sang JSON!**

---

## 🔧 Tool hỗ trợ convert

Nếu có file Netscape format, tool sẽ tự động detect và convert:

```python
# flow_controller.py sẽ tự động handle
if cookies_path.endswith('.txt'):
    # Check if Netscape format
    with open(cookies_path) as f:
        first_line = f.readline()
        if 'Netscape' in first_line:
            # Auto convert to JSON
            cookies = convert_netscape_to_json(cookies_path)
```

---

## ✅ Kiểm tra cookies có hợp lệ

Sau khi có file `cookie.txt`:

```bash
cd /Users/macos/Desktop/VEO2
python test_cookies.py
```

**Script test_cookies.py:**

```python
import json
from src.browser_automation.flow_controller import FlowController
import asyncio

async def test_cookies():
    controller = FlowController(
        cookies_path="./cookie.txt",
        download_dir="./data/test",
        headless=False
    )

    await controller.start()
    success = await controller.goto_flow()

    if success:
        print("✅ Cookies hợp lệ! Đã đăng nhập Flow")
    else:
        print("❌ Cookies không hợp lệ hoặc đã hết hạn")

    await controller.close()

asyncio.run(test_cookies())
```

---

## 🎯 Checklist

- [ ] Cài extension "Get cookies.txt LOCALLY"
- [ ] Đăng nhập https://labs.google/fx/vi/tools/flow
- [ ] Export cookies
- [ ] Di chuyển file vào `/Users/macos/Desktop/VEO2/cookie.txt`
- [ ] Test cookies: `python test_cookies.py`
- [ ] Chạy tool: `python app.py`

---

## ⏰ Cookies hết hạn khi nào?

**Google cookies thường hết hạn sau:**
- 2 tuần (nếu không "Remember me")
- 1 năm (nếu chọn "Stay signed in")

**Khi cookies hết hạn:**
1. Export cookies mới từ browser
2. Thay thế file `cookie.txt`
3. Restart tool

---

## 🆘 Troubleshooting

### Lỗi: "Cookies file not found"
```bash
# Kiểm tra file có tồn tại
ls -la /Users/macos/Desktop/VEO2/cookie.txt

# Nếu không có, export lại từ browser
```

### Lỗi: "Redirected to login page"
```
❌ Cookies đã hết hạn
→ Export cookies mới từ browser
```

### Lỗi: "Invalid JSON format"
```bash
# Kiểm tra format file
cat cookie.txt

# Phải là JSON array:
[
  { "name": "...", "value": "..." }
]
```

---

## 📚 Tài liệu tham khảo

1. **Extension**: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
2. **Format cookies.txt**: http://www.cookiecentral.com/faq/#3.5
3. **Playwright cookies**: https://playwright.dev/python/docs/api/class-browsercontext#browser-context-add-cookies

---

**Sau khi có file `cookie.txt`, tool sẽ tự động login vào Flow!** 🚀
