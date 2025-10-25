"""
Inspect Download UI - Debug the download menu and options
"""
import asyncio
from playwright.async_api import async_playwright

async def inspect_download_ui():
    print("="*60)
    print("INSPECT DOWNLOAD UI")
    print("="*60)

    PROJECT_ID = "559e7aca-ab4c-4f35-9076-fba5a69a18c1"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1728, 'height': 1117},
            device_scale_factor=2
        )

        # Load cookies
        import json
        with open('./config/cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()

        print("\n[1] Navigating to project...")
        project_url = f"https://labs.google/fx/vi/tools/flow/project/{PROJECT_ID}"
        await page.goto(project_url)
        await asyncio.sleep(5)

        print("\n[2] Finding video cards...")
        # Find all divs that might be video cards
        all_text = await page.content()
        if "cherry" in all_text.lower():
            print("   ✅ Found 'cherry' text on page")
        else:
            print("   ❌ No 'cherry' text found")

        print("\n[3] Looking for more_vert buttons...")
        more_vert_buttons = await page.query_selector_all('button')
        count = 0
        for btn in more_vert_buttons:
            try:
                text = await btn.inner_text()
                aria_label = await btn.get_attribute('aria-label') or ""

                if "more_vert" in text.lower() or "more" in aria_label.lower():
                    count += 1
                    print(f"\n   Button #{count}:")
                    print(f"      Text: {text[:50]}")
                    print(f"      Aria-label: {aria_label}")

                    is_visible = await btn.is_visible()
                    print(f"      Visible: {is_visible}")
            except:
                pass

        print(f"\n   Total more_vert-like buttons: {count}")

        print("\n" + "="*60)
        print("MANUAL TESTING")
        print("="*60)
        print("\n⏸️  NOW:")
        print("   1. Find a video card in the browser")
        print("   2. Click the three dots (more options) button")
        print("   3. Look for download option text")
        print("   4. Tell me the EXACT text of the download option")
        print("   5. Press Enter here when done")
        print("="*60)

        input("\nPress Enter after manual inspection...")

        print("\n[4] After you clicked, checking page for download option...")
        await asyncio.sleep(1)

        # Try to find download menu items
        print("\nSearching for download-related elements...")

        # Check all visible text
        all_buttons = await page.query_selector_all('button, div[role="menuitem"], [role="menuitem"]')
        download_keywords = ["tải", "download", "xuống", "save", "lưu"]

        found_download = []
        for elem in all_buttons:
            try:
                text = await elem.inner_text()
                if any(kw in text.lower() for kw in download_keywords):
                    is_visible = await elem.is_visible()
                    tag = await elem.evaluate('el => el.tagName')
                    role = await elem.get_attribute('role') or "N/A"

                    found_download.append({
                        'text': text.strip(),
                        'tag': tag,
                        'role': role,
                        'visible': is_visible
                    })
            except:
                pass

        if found_download:
            print(f"\n✅ Found {len(found_download)} download-related elements:")
            for i, item in enumerate(found_download, 1):
                print(f"\n   #{i}:")
                print(f"      Text: {item['text']}")
                print(f"      Tag: {item['tag']}")
                print(f"      Role: {item['role']}")
                print(f"      Visible: {item['visible']}")
        else:
            print("\n❌ No download-related elements found")
            print("   The menu might have closed")

        # Save HTML for inspection
        html = await page.content()
        with open('./data/logs/download_ui_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n💾 Saved page HTML to: ./data/logs/download_ui_debug.html")

        # Screenshot
        await page.screenshot(path='./data/logs/download_ui_debug.png', full_page=True)
        print("📸 Saved screenshot to: ./data/logs/download_ui_debug.png")

        print("\n[5] Keeping browser open for 30 seconds...")
        await asyncio.sleep(30)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_download_ui())
