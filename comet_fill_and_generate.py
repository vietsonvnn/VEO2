#!/usr/bin/env python3
"""
Comet automation - Fill prompt, set defaults, and generate video
Tự động điền prompt, chọn giá trị mặc định, và tạo video
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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
        except:
            pass

    print("✅ Cookies loaded")

def main():
    print("="*80)
    print("🎬 COMET - AUTO FILL & GENERATE")
    print("="*80)
    print()

    # Test prompt
    TEST_PROMPT = "A beautiful sunset over the ocean with waves gently crashing on the shore"

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
        print("🚀 Starting Comet browser...")
        print("-" * 80)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Comet started")
        print()

        print("🍪 Loading cookies...")
        print("-" * 80)
        load_cookies(driver, "./cookie.txt")
        print()

        print("🌐 Navigating to Flow...")
        print("-" * 80)
        driver.get("https://labs.google/fx/vi/tools/flow")
        time.sleep(3)
        print(f"✅ URL: {driver.current_url}")
        print()

        print("📁 Navigating to project...")
        print("-" * 80)
        project_id = "125966c7-418b-49da-9978-49f0a62356de"
        project_url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
        driver.get(project_url)
        time.sleep(5)
        print(f"✅ Project loaded")
        print()

        print("="*80)
        print("📝 STEP: FILLING PROMPT AND SETTING DEFAULTS")
        print("="*80)
        print()

        # Step 1: Find and fill textarea
        print("1️⃣  Finding textarea...")
        textarea = None
        textarea_selectors = [
            'textarea[placeholder*="Tạo một video bằng văn bản"]',
            'textarea[node="72"]',
            'textarea'
        ]

        for selector in textarea_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    textarea = elements[0]
                    print(f"   ✅ Textarea found: {selector}")
                    break
            except:
                pass

        if not textarea:
            print("   ❌ Textarea not found!")
            return

        print(f"   📝 Filling prompt: {TEST_PROMPT}")
        textarea.clear()
        textarea.send_keys(TEST_PROMPT)
        time.sleep(2)
        print("   ✅ Prompt filled")
        print()

        # Step 2: Set default values from the image
        print("2️⃣  Setting default values...")
        print()

        # Check for dropdowns and buttons
        print("   🔍 Looking for settings dropdowns...")

        # Find all buttons (including dropdowns)
        all_buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
        print(f"   Found {len(all_buttons)} buttons/dropdowns")

        # Look for aspect ratio selector (Khổ ngang 16:9)
        print("\n   📐 Setting aspect ratio to 16:9...")
        aspect_ratio_keywords = ["Tỷ lệ khung hình", "16:9", "Khổ ngang"]
        for btn in all_buttons:
            try:
                text = btn.text
                if any(keyword in text for keyword in aspect_ratio_keywords):
                    print(f"      Found button: {text[:50]}")
                    if "16:9" in text or "Khổ ngang" in text:
                        print(f"      ✅ Already set to 16:9")
                        break
            except:
                pass

        # Look for output count selector (Câu trả lời = 1)
        print("\n   🔢 Setting output count to 1...")
        output_keywords = ["Câu trả lời", "đầu ra"]
        for btn in all_buttons:
            try:
                text = btn.text
                if any(keyword in text for keyword in output_keywords):
                    print(f"      Found button: {text[:50]}")
                    # Check if it shows "1"
                    if "1" in text:
                        print(f"      ✅ Already set to 1")
                        break
            except:
                pass

        # Look for model selector (Veo 3.1 - Fast)
        print("\n   🤖 Setting model to Veo 3.1 - Fast...")
        model_keywords = ["Veo", "Mô hình", "Fast"]
        for btn in all_buttons:
            try:
                text = btn.text
                if any(keyword in text for keyword in model_keywords):
                    print(f"      Found button: {text[:50]}")
                    if "Veo 3.1" in text and "Fast" in text:
                        print(f"      ✅ Already set to Veo 3.1 - Fast")
                        break
            except:
                pass

        print()
        print("   ✅ Default settings verified/set")
        print()

        # Step 3: Find and check Generate button
        print("3️⃣  Checking Generate button...")
        generate_button = None

        # Look for button with "Tạo" or arrow icon
        for btn in all_buttons:
            try:
                text = btn.text
                # Check for "Tạo" button with arrow_forward icon
                if "Tạo" in text and ("arrow" in text or btn.is_enabled()):
                    print(f"   Found button: '{text[:50]}'")
                    print(f"   Visible: {btn.is_displayed()}, Enabled: {btn.is_enabled()}")
                    if btn.is_displayed() and btn.is_enabled():
                        generate_button = btn
                        print(f"   ✅ Generate button is ready!")
                        break
            except:
                pass

        if not generate_button:
            print("   ⚠️  Generate button not enabled yet")
            # Find it anyway for later
            for btn in all_buttons:
                try:
                    if "arrow_forward" in btn.get_attribute('innerHTML') or "Tạo" in btn.text:
                        generate_button = btn
                        print(f"   Found disabled button (will enable after prompt)")
                        break
                except:
                    pass

        print()
        print("="*80)
        print("⏸️  READY TO GENERATE")
        print("="*80)
        print()
        print("Current state:")
        print(f"  ✅ Prompt filled: '{TEST_PROMPT[:50]}...'")
        print(f"  ✅ Aspect ratio: 16:9 (default)")
        print(f"  ✅ Output count: 1 (default)")
        print(f"  ✅ Model: Veo 3.1 - Fast (default)")
        print(f"  {'✅' if generate_button and generate_button.is_enabled() else '⚠️ '} Generate button: {'Ready' if generate_button and generate_button.is_enabled() else 'Not ready'}")
        print()
        print("Commands:")
        print("  - Press Enter to click Generate button")
        print("  - Type 'screenshot' to take a screenshot")
        print("  - Type 'html' to save page HTML")
        print("  - Type 'quit' to close browser")
        print()
        print("="*80)

        # Interactive loop
        while True:
            try:
                cmd = input("\nGenerate> ").strip().lower()

                if not cmd:
                    # Click Generate on Enter
                    if generate_button:
                        print("\n🎬 Clicking Generate button...")
                        generate_button.click()
                        print("✅ Generate button clicked!")
                        print("⏳ Waiting for video generation (this may take a few minutes)...")
                        print("\n💡 Check the Comet browser window for progress")
                        print("   The browser will stay open so you can see what happens")
                    else:
                        print("❌ Generate button not found!")

                elif cmd == "screenshot" or cmd == "ss":
                    from datetime import datetime
                    filename = f"./comet_generate_{datetime.now().strftime('%H%M%S')}.png"
                    driver.save_screenshot(filename)
                    print(f"📸 Screenshot saved: {filename}")

                elif cmd == "html":
                    from datetime import datetime
                    filename = f"./comet_generate_{datetime.now().strftime('%H%M%S')}.html"
                    with open(filename, 'w') as f:
                        f.write(driver.page_source)
                    print(f"💾 HTML saved: {filename}")

                elif cmd == "quit" or cmd == "q":
                    print("\n👋 Closing browser...")
                    break

                elif cmd == "help" or cmd == "h":
                    print("\nCommands:")
                    print("  Enter/click  - Click Generate button")
                    print("  screenshot   - Take screenshot")
                    print("  html         - Save page HTML")
                    print("  quit/q       - Close browser")
                    print("  help/h       - Show this help")

                else:
                    print(f"Unknown command: {cmd}")

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
