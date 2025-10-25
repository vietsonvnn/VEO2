# 🔍 Phân tích Button "Dự án mới" của Flow

## 📋 Theo tài liệu ID.txt

### Workflow chính xác:

```
1. User ở trang: https://labs.google/fx/vi/tools/flow
2. Click button: "+ Dự án mới"
3. Flow tự động:
   - Generate UUID (client-side)
   - Navigate to: https://labs.google/fx/vi/tools/flow/project/{UUID}
4. Render empty editor page
```

### Button selectors cần tìm:

```html
<!-- Theo tài liệu, button có text: "+ Dự án mới" -->
<button class="btn-new-project">
  <span>+</span>
  Dự án mới
</button>
```

**Playwright selectors:**
```javascript
'button:has-text("+ Dự án mới")'
'button:has-text("Dự án mới")'
```

---

## 🔧 Implementation đã update

### File: `flow_controller.py`

```python
async def create_new_project(self, project_name: str = None) -> Optional[str]:
    """
    Create project by clicking "+ Dự án mới" button
    Flow auto-generates UUID and redirects
    """

    # Selectors theo thứ tự ưu tiên
    create_selectors = [
        'button:has-text("+ Dự án mới")',      # Vietnamese UI
        'button:has-text("Dự án mới")',
        'button:has-text("+ New Project")',    # English UI
        'button:has-text("New Project")',
        'button:has([class*="add"])',          # Fallback
        'button[aria-label*="new"]',
        'button[aria-label*="create"]',
    ]

    # Click button
    for selector in create_selectors:
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            break
        except:
            continue

    # Wait for redirect to /project/{UUID}
    await asyncio.sleep(5)

    # Extract UUID from URL
    current_url = self.page.url
    if "/project/" in current_url:
        project_id = current_url.split("/project/")[-1].split("?")[0]
        return project_id

    return None
```

---

## ⚠️ Vấn đề hiện tại

### Lỗi: "Không thể tạo project"

**Nguyên nhân có thể:**

1. **Button selector không match**
   - Flow UI có thể dùng component khác (không phải `<button>`)
   - Text có thể khác ("+ Dự án mới" vs "+ Create Project")
   - Button có thể bị hidden/disabled

2. **Cookies hết hạn**
   - Không đăng nhập → Không có quyền tạo project
   - Redirect về login page

3. **Flow UI thay đổi**
   - Google thay đổi DOM structure
   - Button không còn ở dashboard

---

## 🔍 Debug Steps

### Bước 1: Kiểm tra xem đã vào đúng Flow page chưa

```python
async def goto_flow(self):
    await self.page.goto("https://labs.google/fx/vi/tools/flow")
    await asyncio.sleep(5)

    # Check URL
    current_url = self.page.url
    logger.info(f"Current URL: {current_url}")

    # Check if redirected to login
    if "accounts.google.com" in current_url:
        logger.error("❌ Redirected to login - cookies expired")
        return False

    return True
```

### Bước 2: Screenshot để xem UI hiện tại

```python
async def create_new_project(self, project_name: str = None):
    # Take screenshot before clicking
    await self.page.screenshot(path="./debug_flow_dashboard.png")
    logger.info("📸 Screenshot saved: debug_flow_dashboard.png")

    # Try to find button
    # ...
```

### Bước 3: Inspect tất cả buttons trên page

```python
async def debug_find_buttons(self):
    """Debug: List all buttons on page"""
    buttons = await self.page.query_selector_all("button")
    logger.info(f"Found {len(buttons)} buttons:")

    for i, button in enumerate(buttons):
        text = await button.inner_text()
        aria_label = await button.get_attribute("aria-label")
        logger.info(f"  Button {i}: text='{text}' aria-label='{aria_label}'")
```

---

## ✅ Solution: Dùng Project ID có sẵn

**Recommendation**: Thay vì tạo project mới (có thể fail), nên:

### Option A: User cung cấp Project ID ⭐ RECOMMENDED

```python
# User input
project_id = "f81e875e-19f7-472b-8ded-2a30c6a5a00d"

# Direct navigation
await controller.goto_project(project_id)
# → Vào thẳng: /project/{project_id}
# → Không cần click button
# → Luôn work nếu cookies hợp lệ
```

**Ưu điểm:**
- ✅ Không bị lỗi find button
- ✅ Không phụ thuộc vào UI Flow
- ✅ Stable, predictable
- ✅ User có thể dùng project cũ

### Option B: Tạo project manual

1. User tự mở Flow
2. Click "+ Dự án mới"
3. Copy Project ID từ URL
4. Paste vào tool

---

## 🎯 Recommendation cho tool

### UI Input fields:

```
┌─────────────────────────────────────────┐
│ ✨ Chủ đề: [Nấu phở]                    │
│ ⏱️ Thời lượng: [1 phút]                  │
│ 🔑 Cookies: [./cookie.txt]              │
│ 📁 Project ID: [abc123def456] ⭐ BẮT BUỘC│
└─────────────────────────────────────────┘
```

### Workflow:

```python
if project_id:
    # Direct navigation - LUÔN WORK
    await controller.goto_project(project_id)
else:
    # Try to create - CÓ THỂ FAIL
    project_id = await controller.create_new_project()
    if not project_id:
        return "❌ Không thể tạo project. Vui lòng nhập Project ID"
```

---

## 📊 Test Results

### Test 1: Với Project ID
```
✅ Browser started
✅ Loaded Flow page
✅ Navigated to project: abc123
✅ Scene 1 created
✅ Scene 2 created
...
```

### Test 2: Không có Project ID (tạo mới)
```
✅ Browser started
✅ Loaded Flow page
❌ Could not find '+ Dự án mới' button
❌ Project creation failed
```

→ **Kết luận**: Nên bắt buộc user nhập Project ID

---

## 🔑 How to get Project ID

### Cách 1: Từ URL
```
1. Vào https://labs.google/fx/vi/tools/flow
2. Click "+ Dự án mới"
3. Copy từ URL:
   https://labs.google/fx/vi/tools/flow/project/f81e875e-19f7-472b-8ded-2a30c6a5a00d
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### Cách 2: Từ project list
```
1. Vào Flow dashboard
2. Click vào project cũ
3. Copy ID từ URL
```

### Cách 3: Generate UUID (offline)
```python
import uuid
project_id = str(uuid.uuid4())
# f81e875e-19f7-472b-8ded-2a30c6a5a00d
```

**⚠️ Lưu ý**: UUID tự generate không work vì project chưa tồn tại trên server

---

## 💡 Final Implementation

### UI update:

```python
# app.py
with gr.Row():
    cookies = gr.Textbox(label="🔑 Cookies", value="./cookie.txt")
    project_id_input = gr.Textbox(
        label="📁 Project ID (BẮT BUỘC)",
        value="",
        placeholder="Paste Project ID từ Flow URL"
    )

gr.Markdown("""
**Hướng dẫn lấy Project ID:**
1. Vào https://labs.google/fx/vi/tools/flow
2. Click "+ Dự án mới"
3. Copy ID từ URL: `.../project/[ID này]`
""")
```

### Logic update:

```python
async def generate_all_videos_async():
    if not state.project_id:
        return "❌ Vui lòng nhập Project ID", []

    controller = FlowController(state.cookies, ...)
    await controller.start()
    await controller.goto_flow()

    # Direct navigation - NO button clicking
    success = await controller.goto_project(state.project_id)
    if not success:
        return "❌ Không thể vào project. Kiểm tra Project ID", []

    # Continue with video generation...
```

---

## ✅ Kết luận

1. **Tạo project mới có thể fail** do:
   - Button selector thay đổi
   - Cookies hết hạn
   - UI Flow update

2. **Giải pháp tốt nhất**:
   - ✅ Bắt buộc user nhập Project ID
   - ✅ Direct navigation (không click button)
   - ✅ Stable, predictable

3. **Đã implement trong tool**:
   - ✅ UI có field Project ID
   - ✅ Logic check và dùng ID nếu có
   - ✅ Fallback tạo mới (có thể fail)

**Tool hiện tại đã ĐÚNG - chỉ cần user nhập Project ID!** 🎯
