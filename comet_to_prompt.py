#!/usr/bin/env python3
"""
Comet automation - Stop at prompt input step
Tự động vào Flow project và dừng lại tại bước nhập prompt
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def load_cookies(driver, cookie_file):
    """Load cookies from JSON file"""
    print(f"📂 Loading cookies from {cookie_file}...")

    with open(cookie_file, 'r') as f:
        cookies = json.load(f)

    driver.get("https://labs.google")
    time.sleep(2)

    for cookie in cookies:
        selenium_cookie = {
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie['domain'],
            'path': cookie.get('path', '/'),
        }

        if 'expiry' in cookie:
            selenium_cookie['expiry'] = int(cookie['expiry'])
        if 'secure' in cookie:
            selenium_cookie['secure'] = cookie['secure']
        if 'httpOnly' in cookie:
            selenium_cookie['httpOnly'] = cookie['httpOnly']
        if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
            selenium_cookie['sameSite'] = cookie['sameSite']

        try:
            driver.add_cookie(selenium_cookie)
        except Exception as e:
            pass

    print("✅ Cookies loaded")

def main():
    print("="*80)
    print("🎬 COMET - AUTO TO PROMPT INPUT")
    print("="*80)
    print()

    # Configure Comet
    options = Options()
    options.binary_location = "/Applications/Comet.app/Contents/MacOS/Comet"
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = None

    try:
        print("🚀 Step 1: Starting Comet browser...")
        print("-" * 80)
        print("   📥 Installing/updating ChromeDriver to match Comet version...")

        # Use webdriver-manager to auto-download the correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print("✅ Comet started with matching ChromeDriver")
        print()

        print("🍪 Step 2: Loading cookies...")
        print("-" * 80)
        load_cookies(driver, "./cookie.txt")
        print()

        print("🌐 Step 3: Navigating to Flow...")
        print("-" * 80)
        driver.get("https://labs.google/fx/vi/tools/flow")
        time.sleep(3)
        print(f"✅ URL: {driver.current_url}")
        print()

        print("📁 Step 4: Navigating to project...")
        print("-" * 80)
        project_id = "125966c7-418b-49da-9978-49f0a62356de"
        project_url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
        driver.get(project_url)
        time.sleep(5)  # Wait for page to load
        print(f"✅ Project loaded: {project_id}")
        print()

        print("🔍 Step 5: Looking for prompt textarea...")
        print("-" * 80)

        # Try to find textarea
        textarea_selectors = [
            'textarea[node="72"]',
            'textarea[placeholder*="Tạo một video bằng văn bản"]',
            'textarea[placeholder*="Tạo một video"]',
            'textarea'
        ]

        textarea = None
        for selector in textarea_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   Found {len(elements)} textareas with selector: {selector}")
                    textarea = elements[0]
                    break
            except:
                pass

        if textarea:
            print(f"✅ Textarea found!")
            print(f"   Tag: {textarea.tag_name}")
            print(f"   Placeholder: {textarea.get_attribute('placeholder')}")
            is_visible = textarea.is_displayed()
            is_enabled = textarea.is_enabled()
            print(f"   Visible: {is_visible}")
            print(f"   Enabled: {is_enabled}")
        else:
            print("⚠️  Textarea not found")
        print()

        # Look for generate button
        print("🔍 Step 6: Looking for Generate button...")
        print("-" * 80)

        button_selectors = [
            'button:has-text("Tạo")',
            'button[aria-label*="Tạo"]',
            'button'
        ]

        buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
        print(f"   Found {len(buttons)} buttons on page")

        # Find "Tạo" button
        tao_button = None
        for btn in buttons:
            try:
                text = btn.text
                if "Tạo" in text or "tạo" in text.lower():
                    print(f"   - Button with text: '{text}' (visible={btn.is_displayed()}, enabled={btn.is_enabled()})")
                    if btn.is_displayed() and btn.is_enabled():
                        tao_button = btn
            except:
                pass

        if tao_button:
            print(f"✅ Generate button found and ready!")
        else:
            print("⚠️  Generate button not found or not ready")
        print()

        # PAUSE AT PROMPT INPUT STEP
        print("="*80)
        print("⏸️  PAUSED AT PROMPT INPUT STEP")
        print("="*80)
        print()
        print("🎯 You are now at the prompt input step!")
        print()
        print("Current page state:")
        print(f"  - URL: {driver.current_url}")
        print(f"  - Title: {driver.title}")
        print(f"  - Textarea found: {textarea is not None}")
        print(f"  - Generate button found: {tao_button is not None}")
        print()
        print("What you can do now:")
        print("  1. Inspect the Comet browser window")
        print("  2. Check the Flow UI layout and elements")
        print("  3. Manually type in the textarea to test")
        print("  4. Click the Generate button manually")
        print()
        print("Debug commands:")
        print("  - Press Enter to take a screenshot")
        print("  - Type 'fill <text>' to fill textarea with text")
        print("  - Type 'click' to click Generate button")
        print("  - Type 'screenshot' to take a screenshot")
        print("  - Type 'html' to save page HTML")
        print("  - Type 'quit' to close browser")
        print()
        print("="*80)

        # Interactive loop
        while True:
            try:
                cmd = input("\nPrompt-Debug> ").strip()

                if not cmd or cmd.lower() == "screenshot" or cmd.lower() == "ss":
                    from datetime import datetime
                    filename = f"./comet_prompt_{datetime.now().strftime('%H%M%S')}.png"
                    driver.save_screenshot(filename)
                    print(f"📸 Screenshot saved: {filename}")

                elif cmd.lower() == "quit" or cmd.lower() == "q":
                    print("\n👋 Closing browser...")
                    break

                elif cmd.lower().startswith("fill "):
                    if textarea:
                        text = cmd[5:].strip()
                        textarea.clear()
                        textarea.send_keys(text)
                        print(f"✅ Filled textarea with: {text}")
                    else:
                        print("❌ Textarea not found!")

                elif cmd.lower() == "click":
                    if tao_button:
                        tao_button.click()
                        print("✅ Clicked Generate button!")
                        print("⏳ Waiting for video generation...")
                    else:
                        print("❌ Generate button not found!")

                elif cmd.lower() == "html":
                    from datetime import datetime
                    filename = f"./comet_page_{datetime.now().strftime('%H%M%S')}.html"
                    with open(filename, 'w') as f:
                        f.write(driver.page_source)
                    print(f"💾 HTML saved: {filename}")

                elif cmd.lower() == "help" or cmd.lower() == "h":
                    print("\nCommands:")
                    print("  screenshot/ss    - Take screenshot")
                    print("  fill <text>      - Fill textarea with text")
                    print("  click            - Click Generate button")
                    print("  html             - Save page HTML")
                    print("  quit/q           - Close browser")
                    print("  help/h           - Show this help")

                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted...")
                break

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
            print("\n✅ Browser closed")
        print("="*80)

if __name__ == "__main__":
    print()
    main()
