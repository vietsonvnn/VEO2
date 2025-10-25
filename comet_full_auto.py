#!/usr/bin/env python3
"""
COMET FULL AUTOMATION - Complete workflow
1. Navigate to project
2. Fill prompt
3. Set output count to 1 (if needed)
4. Click Generate
5. Wait for completion
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
from datetime import datetime

def load_cookies(driver, cookie_file):
    """Load cookies"""
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
    driver.get("https://labs.google")
    time.sleep(2)
    for cookie in cookies:
        c = {'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain'], 'path': cookie.get('path', '/')}
        if 'expiry' in cookie: c['expiry'] = int(cookie['expiry'])
        if 'secure' in cookie: c['secure'] = cookie['secure']
        if 'httpOnly' in cookie: c['httpOnly'] = cookie['httpOnly']
        if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']: c['sameSite'] = cookie['sameSite']
        try: driver.add_cookie(c)
        except: pass

def main():
    TEST_PROMPT = "A beautiful sunset over the ocean with waves gently crashing on the shore"

    print("="*80)
    print("🎬 COMET FULL AUTOMATION TEST")
    print("="*80)
    print(f"\n📝 Prompt: {TEST_PROMPT}")
    print(f"🎯 Target: 1 video (not 2)")
    print("="*80 + "\n")

    options = Options()
    options.binary_location = "/Applications/Comet.app/Contents/MacOS/Comet"
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        print("🚀 Step 1: Starting Comet...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Comet started\n")

        print("🍪 Step 2: Loading cookies...")
        load_cookies(driver, "./cookie.txt")
        print("✅ Cookies loaded\n")

        print("🌐 Step 3: Navigating to project...")
        project_url = "https://labs.google/fx/vi/tools/flow/project/125966c7-418b-49da-9978-49f0a62356de"
        driver.get(project_url)
        time.sleep(5)
        print("✅ Project loaded\n")

        print("📝 Step 4: Filling prompt...")
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Tạo một video"]')
        textarea.clear()
        time.sleep(0.5)
        textarea.send_keys(TEST_PROMPT)
        time.sleep(2)
        print(f"✅ Prompt filled: {TEST_PROMPT[:50]}...\n")

        # Check current x2/x1 setting
        print("🔍 Step 5: Checking output count setting...")
        try:
            x_count = driver.find_element(By.XPATH, "//*[contains(text(), 'x2') or contains(text(), 'x1')]")
            current_count = x_count.text.strip()
            print(f"   Current setting: {current_count}")

            if current_count == "x2":
                print("   ⚠️  Need to change from x2 to x1!")
                print("   🔧 Opening settings dialog...")

                # Find and click Settings button
                settings_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Cài đặt"]')
                settings_btn.click()
                time.sleep(2)
                print("   ✅ Settings dialog opened")

                # Take screenshot of settings
                screenshot1 = f"./comet_settings_before_{datetime.now().strftime('%H%M%S')}.png"
                driver.save_screenshot(screenshot1)
                print(f"   📸 Screenshot: {screenshot1}")

                # TODO: Find the control to change x2 to x1
                # This depends on the actual settings dialog UI
                print("   ⚠️  Manual intervention needed: Change x2 to x1 in the dialog")
                print("   Press Enter when done...")
                input()

            elif current_count == "x1":
                print("   ✅ Already set to x1!")
            else:
                print(f"   ℹ️  Found: {current_count}")

        except Exception as e:
            print(f"   ⚠️  Could not find x2/x1 indicator: {e}")
            print("   Assuming default settings...\n")

        print("\n🎬 Step 6: Looking for Generate button...")
        generate_btn = None
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button')

        for btn in buttons:
            try:
                # Look for button with "Tạo" text and arrow_forward icon
                inner_text = btn.text
                inner_html = btn.get_attribute('innerHTML')

                if "Tạo" in inner_text and "arrow_forward" in inner_html:
                    if btn.is_displayed() and btn.is_enabled():
                        generate_btn = btn
                        print(f"   ✅ Found Generate button (enabled)")
                        break
                    else:
                        print(f"   Found Generate button but disabled={not btn.is_enabled()}, visible={btn.is_displayed()}")
            except:
                pass

        if not generate_btn:
            print("   ❌ Generate button not found or not ready!")
            print("   Taking screenshot for debug...")
            screenshot2 = f"./comet_no_generate_{datetime.now().strftime('%H%M%S')}.png"
            driver.save_screenshot(screenshot2)
            print(f"   📸 {screenshot2}")
            return

        print("\n🚀 Step 7: Clicking Generate button...")
        generate_btn.click()
        print("✅ Generate button clicked!")
        time.sleep(3)

        screenshot3 = f"./comet_after_generate_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(screenshot3)
        print(f"📸 {screenshot3}\n")

        print("⏳ Step 8: Waiting for video generation...")
        print("   Checking for video generation progress...\n")

        # Wait and monitor
        max_wait = 180  # 3 minutes
        start_time = time.time()
        last_check = 0

        while (time.time() - start_time) < max_wait:
            try:
                # Look for progress indicators or completion
                progress_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '%')]")

                if progress_elements:
                    progress_texts = [elem.text for elem in progress_elements if elem.text.strip()]
                    if progress_texts:
                        elapsed = int(time.time() - start_time)
                        if elapsed - last_check >= 10:  # Log every 10 seconds
                            print(f"   [{elapsed}s] Progress: {', '.join(progress_texts)}")
                            last_check = elapsed

                # Check for completion (video element or play button)
                videos = driver.find_elements(By.CSS_SELECTOR, 'video[src]')
                if videos:
                    print(f"\n✅ Video generation complete!")
                    print(f"   Found {len(videos)} video(s)")

                    screenshot4 = f"./comet_completed_{datetime.now().strftime('%H%M%S')}.png"
                    driver.save_screenshot(screenshot4)
                    print(f"   📸 {screenshot4}")
                    break

                time.sleep(5)

            except Exception as e:
                print(f"   Error during wait: {e}")
                time.sleep(5)

        print("\n" + "="*80)
        print("✅ AUTOMATION COMPLETE")
        print("="*80)
        print("\n💡 Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

        # Take error screenshot
        if driver:
            try:
                error_screenshot = f"./comet_error_{datetime.now().strftime('%H%M%S')}.png"
                driver.save_screenshot(error_screenshot)
                print(f"📸 Error screenshot: {error_screenshot}")
            except:
                pass

    finally:
        if driver:
            driver.quit()
            print("\n✅ Browser closed")
        print("="*80)

if __name__ == "__main__":
    main()
