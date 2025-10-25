#!/usr/bin/env python3
"""
Comet automation - Set exact settings from image
Điền prompt và set đúng settings: 16:9, 1 video, Veo 3.1 Fast
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def load_cookies(driver, cookie_file):
    """Load cookies"""
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
    print("🎬 COMET - SET EXACT SETTINGS")
    print("="*80)
    print()

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
        print("🚀 Starting Comet...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Comet started")
        print()

        print("🍪 Loading cookies...")
        load_cookies(driver, "./cookie.txt")
        print()

        print("🌐 Navigating to Flow project...")
        project_id = "125966c7-418b-49da-9978-49f0a62356de"
        project_url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
        driver.get(project_url)
        time.sleep(5)
        print(f"✅ Project loaded")
        print()

        print("="*80)
        print("⚙️  SETTING UP CONFIGURATION")
        print("="*80)
        print()

        # Step 1: Fill prompt
        print("1️⃣  Filling prompt...")
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Tạo một video bằng văn bản"]')
        textarea.clear()
        textarea.send_keys(TEST_PROMPT)
        time.sleep(1)
        print(f"   ✅ Prompt filled: {TEST_PROMPT[:50]}...")
        print()

        # Step 2: Find and click settings dropdowns
        print("2️⃣  Looking for settings dropdowns...")
        print()

        # Get all buttons that might be dropdowns (have role="combobox" or aria-expanded)
        all_buttons = driver.find_elements(By.CSS_SELECTOR, 'button')

        # Find dropdown buttons by looking for specific text
        aspect_ratio_btn = None
        output_count_btn = None
        model_btn = None

        for btn in all_buttons:
            try:
                text = btn.text.strip()

                # Aspect ratio dropdown - contains "16:9" or "Khổ ngang"
                if "16:9" in text or "Khổ ngang" in text:
                    print(f"   📐 Found aspect ratio dropdown: '{text[:60]}'")
                    aspect_ratio_btn = btn

                # Output count dropdown - should show a number
                # Look for button near text "Câu trả lời đầu ra"
                if text.isdigit() and len(text) <= 2:
                    # This might be the output count
                    print(f"   🔢 Found possible output count: '{text}'")
                    if text != "1":
                        output_count_btn = btn

                # Model dropdown - contains "Veo"
                if "Veo" in text and ("Fast" in text or "Quality" in text):
                    print(f"   🤖 Found model dropdown: '{text[:60]}'")
                    model_btn = btn

            except:
                pass

        print()

        # Step 3: Set output count to 1
        if output_count_btn:
            print("3️⃣  Setting output count to 1...")
            print(f"   Current value: {output_count_btn.text}")
            print(f"   Clicking dropdown...")
            output_count_btn.click()
            time.sleep(1)

            # Look for option "1" in the dropdown menu
            try:
                # Try to find menu items
                menu_items = driver.find_elements(By.CSS_SELECTOR, '[role="menuitem"], [role="option"]')
                for item in menu_items:
                    if item.text == "1":
                        print(f"   Clicking option '1'...")
                        item.click()
                        time.sleep(1)
                        print(f"   ✅ Output count set to 1")
                        break
            except Exception as e:
                print(f"   ⚠️  Could not set output count: {e}")
        else:
            print("3️⃣  Output count already at 1 or not found")

        print()

        # Step 4: Verify aspect ratio (16:9)
        if aspect_ratio_btn:
            current = aspect_ratio_btn.text
            if "16:9" in current:
                print("4️⃣  Aspect ratio: ✅ Already set to 16:9")
            else:
                print(f"4️⃣  Aspect ratio: Current = {current}, need to change...")
                # Click to open dropdown
                aspect_ratio_btn.click()
                time.sleep(1)
                # Look for 16:9 option
                try:
                    options = driver.find_elements(By.CSS_SELECTOR, '[role="menuitem"], [role="option"]')
                    for opt in options:
                        if "16:9" in opt.text:
                            opt.click()
                            time.sleep(1)
                            print("   ✅ Set to 16:9")
                            break
                except:
                    pass
        else:
            print("4️⃣  Aspect ratio: Not found (may be default)")

        print()

        # Step 5: Verify model (Veo 3.1 - Fast)
        if model_btn:
            current = model_btn.text
            if "Veo 3.1" in current and "Fast" in current:
                print("5️⃣  Model: ✅ Already set to Veo 3.1 - Fast")
            else:
                print(f"5️⃣  Model: Current = {current}, need to change...")
                # Click to open dropdown
                model_btn.click()
                time.sleep(1)
                # Look for Veo 3.1 - Fast option
                try:
                    options = driver.find_elements(By.CSS_SELECTOR, '[role="menuitem"], [role="option"]')
                    for opt in options:
                        if "Veo 3.1" in opt.text and "Fast" in opt.text:
                            opt.click()
                            time.sleep(1)
                            print("   ✅ Set to Veo 3.1 - Fast")
                            break
                except:
                    pass
        else:
            print("5️⃣  Model: Not found (may be default)")

        print()
        print("="*80)
        print("✅ SETTINGS CONFIGURED")
        print("="*80)
        print()
        print("Current configuration:")
        print(f"  📝 Prompt: {TEST_PROMPT[:50]}...")
        print(f"  📐 Aspect ratio: 16:9")
        print(f"  🔢 Output count: 1")
        print(f"  🤖 Model: Veo 3.1 - Fast")
        print()
        print("Commands:")
        print("  - Press Enter to click Generate")
        print("  - Type 'screenshot' to take screenshot")
        print("  - Type 'quit' to close")
        print()
        print("="*80)

        # Interactive
        while True:
            try:
                cmd = input("\nGenerate> ").strip().lower()

                if not cmd:
                    print("\n🎬 Looking for Generate button...")
                    buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
                    for btn in buttons:
                        try:
                            if "Tạo" in btn.text and btn.is_enabled():
                                print("✅ Found Generate button, clicking...")
                                btn.click()
                                print("✅ Clicked! Video generation started")
                                print("⏳ Check Comet window for progress...")
                                break
                        except:
                            pass

                elif cmd == "screenshot" or cmd == "ss":
                    from datetime import datetime
                    filename = f"./comet_settings_{datetime.now().strftime('%H%M%S')}.png"
                    driver.save_screenshot(filename)
                    print(f"📸 Screenshot: {filename}")

                elif cmd == "quit" or cmd == "q":
                    break

                else:
                    print(f"Unknown: {cmd}")

            except KeyboardInterrupt:
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
