"""
Manual Login Test - Đăng nhập thủ công và lưu cookies
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def manual_login():
    print("="*60)
    print("MANUAL LOGIN TEST")
    print("="*60)
    print("\nBrowser sẽ mở ra.")
    print("Bạn hãy:")
    print("  1. Đăng nhập vào Google Labs Flow")
    print("  2. Đợi trang load xong")
    print("  3. Nhấn Enter ở terminal này để lưu cookies")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        print("\n[1] Opening Flow...")
        await page.goto("https://labs.google/fx/vi/tools/flow")

        print("\n[2] Vui lòng đăng nhập trong browser...")
        print("    Sau khi đăng nhập xong, quay lại terminal và nhấn Enter")

        # Wait for user input
        input("\nNhấn Enter sau khi đã đăng nhập... ")

        print("\n[3] Saving cookies...")
        cookies = await context.cookies()

        # Save to file
        with open('./config/cookies.json', 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Saved {len(cookies)} cookies to ./config/cookies.json")

        # Show preview of cookies
        print("\nCookie preview:")
        for cookie in cookies[:5]:
            print(f"  - {cookie['name']}: {cookie['value'][:20]}...")

        await browser.close()

        print("\n" + "="*60)
        print("✅ COOKIES SAVED!")
        print("="*60)
        print("\nBây giờ có thể chạy test:")
        print("  python3 test_browser_quick.py")

if __name__ == "__main__":
    asyncio.run(manual_login())
