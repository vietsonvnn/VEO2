"""
Create Project and Inspect - Tạo project rồi inspect DOM
"""
import asyncio
from playwright.async_api import async_playwright

async def create_project_and_inspect():
    print("="*60)
    print("CREATE PROJECT & INSPECT SELECTORS")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})

        # Load cookies
        import json
        with open('./config/cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()

        print("\n[1] Opening Flow...")
        await page.goto("https://labs.google/fx/vi/tools/flow")
        await asyncio.sleep(5)

        print("\n[2] Looking for 'Add Starter Projects' or 'New Project' button...")

        # Try to find and click the project creation button
        project_button_selectors = [
            "button:has-text('Add Starter Projects')",
            "button:has-text('New Project')",
            "button:has-text('Create')",
            "[aria-label*='project']",
            "button:has-text('+')",
        ]

        clicked = False
        for selector in project_button_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"   ✅ Found button: {selector}")

                    # Check if visible
                    is_visible = await element.is_visible()
                    if is_visible:
                        print(f"   📍 Button is visible, but NOT clicking automatically")
                        print(f"   ⚠️  Please click manually to create project")
                        break
            except Exception as e:
                continue

        print("\n" + "="*60)
        print("⏸️  VUI LÒNG:")
        print("   1. Click vào 'Add Starter Projects' hoặc tạo project mới")
        print("   2. Đợi project page mở ra")
        print("   3. Bạn sẽ thấy chỗ nhập Prompt")
        print("   4. Quay lại terminal và nhấn Enter")
        print("="*60)

        input("\nNhấn Enter sau khi project đã mở...")

        print("\n[3] Inspecting project page DOM...")
        await asyncio.sleep(2)

        # Find all textareas
        print("\n📝 TEXTAREAS:")
        textareas = await page.query_selector_all("textarea")
        print(f"   Found {len(textareas)} textarea(s)")

        for i, ta in enumerate(textareas):
            try:
                placeholder = await ta.get_attribute("placeholder") or ""
                aria_label = await ta.get_attribute("aria-label") or ""
                id_attr = await ta.get_attribute("id") or ""
                name = await ta.get_attribute("name") or ""

                print(f"\n   Textarea #{i+1}:")
                if placeholder:
                    print(f"      Placeholder: {placeholder}")
                if aria_label:
                    print(f"      Aria-label: {aria_label}")
                if id_attr:
                    print(f"      ID: {id_attr}")
                if name:
                    print(f"      Name: {name}")
            except:
                pass

        # Find all buttons
        print("\n\n🔘 BUTTONS (first 15):")
        buttons = await page.query_selector_all("button")
        print(f"   Found {len(buttons)} button(s) total")

        button_count = 0
        for btn in buttons:
            try:
                text = await btn.inner_text()
                aria_label = await btn.get_attribute("aria-label") or ""

                if text.strip() or aria_label:
                    button_count += 1
                    print(f"\n   Button #{button_count}:")
                    if text.strip():
                        print(f"      Text: {text.strip()}")
                    if aria_label:
                        print(f"      Aria-label: {aria_label}")

                    if button_count >= 15:
                        break
            except:
                pass

        # Look for common generate/create button texts
        print("\n\n🔍 Looking for Generate/Create buttons:")
        generate_keywords = ["generate", "create", "tạo", "Generate", "Create"]

        for keyword in generate_keywords:
            try:
                selector = f"button:has-text('{keyword}')"
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    text = await element.inner_text()
                    print(f"   ✅ Found: button:has-text('{keyword}') - Visible: {is_visible} - Text: '{text.strip()}'")
            except:
                pass

        # Save page HTML
        html = await page.content()
        with open('./data/logs/flow_project_dom.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n\n💾 Saved: ./data/logs/flow_project_dom.html")

        # Screenshot
        await page.screenshot(path='./data/logs/flow_project_screenshot.png', full_page=True)
        print("📸 Saved: ./data/logs/flow_project_screenshot.png")

        # Current URL
        print(f"\n🔗 Current URL: {page.url}")

        print("\n" + "="*60)
        print("✅ INSPECTION DONE!")
        print("="*60)
        print("\nThông tin để update code:")
        print("  1. Textarea selector để nhập prompt")
        print("  2. Button selector để click Generate")
        print("  3. Xem file HTML nếu cần thêm thông tin")
        print("="*60)

        print("\n[4] Browser sẽ mở trong 60 giây để bạn inspect thêm...")
        await asyncio.sleep(60)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(create_project_and_inspect())
