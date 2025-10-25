"""
Inspect Flow DOM - Tìm selectors chính xác cho Flow UI
"""
import asyncio
from playwright.async_api import async_playwright

async def inspect_flow_dom():
    print("="*60)
    print("INSPECT FLOW DOM - TÌM SELECTORS")
    print("="*60)
    print("\n📝 Script sẽ:")
    print("   1. Mở Flow với cookies")
    print("   2. Chờ bạn tạo project mới")
    print("   3. Inspect DOM để tìm selectors")
    print("   4. In ra thông tin về các elements quan trọng")
    print("="*60)

    async with async_playwright() as p:
        print("\n[1] Launching browser...")
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        # Load cookies
        import json
        with open('./config/cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()

        print("[2] Opening Flow...")
        await page.goto("https://labs.google/fx/vi/tools/flow")

        print("\n" + "="*60)
        print("⏸️  ĐANG DỪNG LẠI - VUI LÒNG:")
        print("   1. Tạo một project MỚI trong Flow")
        print("   2. Đợi project page load xong")
        print("   3. Quay lại terminal này")
        print("="*60)

        input("\nNhấn Enter sau khi đã tạo project và page đã load...")

        print("\n[3] Inspecting DOM...")

        # Get all textareas
        print("\n📋 TEXTAREAS found:")
        textareas = await page.query_selector_all("textarea")
        for i, ta in enumerate(textareas):
            try:
                placeholder = await ta.get_attribute("placeholder") or "N/A"
                aria_label = await ta.get_attribute("aria-label") or "N/A"
                name = await ta.get_attribute("name") or "N/A"
                class_name = await ta.get_attribute("class") or "N/A"

                print(f"\n   Textarea #{i+1}:")
                print(f"   - Placeholder: {placeholder}")
                print(f"   - Aria-label: {aria_label}")
                print(f"   - Name: {name}")
                print(f"   - Class: {class_name[:100]}")
            except:
                pass

        # Get all buttons
        print("\n\n🔘 BUTTONS found:")
        buttons = await page.query_selector_all("button")
        for i, btn in enumerate(buttons[:10]):  # First 10 buttons
            try:
                text = await btn.inner_text()
                aria_label = await btn.get_attribute("aria-label") or "N/A"
                class_name = await btn.get_attribute("class") or "N/A"

                if text.strip():
                    print(f"\n   Button #{i+1}:")
                    print(f"   - Text: {text.strip()}")
                    print(f"   - Aria-label: {aria_label}")
                    print(f"   - Class: {class_name[:100]}")
            except:
                pass

        # Look for specific Flow UI elements
        print("\n\n🔍 SEARCHING for specific elements:")

        # Try to find prompt input
        prompt_selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "[placeholder*='prompt']",
            "[placeholder*='Prompt']",
            "[aria-label*='prompt']",
            "[aria-label*='Prompt']",
        ]

        for selector in prompt_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"   ✅ Found with selector: {selector}")
            except:
                pass

        # Save page HTML for manual inspection
        html = await page.content()
        with open('./data/logs/flow_project_page.html', 'w', encoding='utf-8') as f:
            f.write(html)

        print("\n\n💾 Saved page HTML to: ./data/logs/flow_project_page.html")

        # Take screenshot
        await page.screenshot(path='./data/logs/flow_project_page.png', full_page=True)
        print("📸 Saved screenshot to: ./data/logs/flow_project_page.png")

        print("\n\n" + "="*60)
        print("🔍 MANUAL INSPECTION:")
        print("   - Mở file flow_project_page.html")
        print("   - Tìm textarea/input để nhập prompt")
        print("   - Tìm button Generate")
        print("   - Gửi cho tôi selector chính xác")
        print("="*60)

        print("\n[4] Keeping browser open for 60 seconds...")
        print("    (Để bạn có thể inspect thêm)")
        await asyncio.sleep(60)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_flow_dom())
