"""
Auto Save Cookies - Mở browser, đợi 60s để login, rồi tự động lưu cookies
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def auto_save_cookies():
    print("="*60)
    print("AUTO COOKIE SAVER")
    print("="*60)
    print("\n🚀 Browser sẽ mở trong 3 giây...")
    print("📝 Bạn có 90 giây để:")
    print("   1. Đăng nhập Google Labs Flow")
    print("   2. Tạo project mới (nếu cần)")
    print("   3. Đợi trang load xong")
    print("\n⏰ Script sẽ TỰ ĐỘNG lưu cookies sau 90 giây")
    print("="*60)

    await asyncio.sleep(3)

    async with async_playwright() as p:
        print("\n[1] Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        page = await context.new_page()

        print("[2] Opening Flow...")
        await page.goto("https://labs.google/fx/vi/tools/flow")

        print("\n⏰ Đang đợi 90 giây để bạn đăng nhập và tạo project...")
        print("   (Hãy đăng nhập và tạo project ngay bây giờ!)")

        # Countdown
        for i in range(90, 0, -15):
            print(f"   ⏳ Còn {i} giây...")
            await asyncio.sleep(15)

        print("\n[3] Saving cookies...")
        cookies = await context.cookies()

        # Save to file
        import os
        os.makedirs('./config', exist_ok=True)

        with open('./config/cookies.json', 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Saved {len(cookies)} cookies to ./config/cookies.json")

        # Show important cookies
        print("\n📋 Cookie summary:")
        cookie_domains = {}
        for cookie in cookies:
            domain = cookie['domain']
            cookie_domains[domain] = cookie_domains.get(domain, 0) + 1

        for domain, count in cookie_domains.items():
            print(f"   - {domain}: {count} cookies")

        # Check for session cookies
        session_cookies = [c for c in cookies if '__Secure-next-auth.session-token' in c['name']]
        if session_cookies:
            print("\n✅ Found authentication session token!")
        else:
            print("\n⚠️  Warning: No session token found. May need to login again.")

        print("\n[4] Closing browser in 5 seconds...")
        await asyncio.sleep(5)
        await browser.close()

        print("\n" + "="*60)
        print("✅ DONE! Cookies saved to ./config/cookies.json")
        print("="*60)
        print("\n🧪 Test cookies với:")
        print("   source venv/bin/activate")
        print("   python3 test_browser_quick.py")

if __name__ == "__main__":
    asyncio.run(auto_save_cookies())
