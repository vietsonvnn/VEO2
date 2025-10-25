#!/usr/bin/env python3
"""
Comet - Click Settings button to change x2 to x1
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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
    print("="*80)
    print("🎬 COMET - CLICK SETTINGS TO CHANGE X2 → X1")
    print("="*80)

    options = Options()
    options.binary_location = "/Applications/Comet.app/Contents/MacOS/Comet"
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = None
    try:
        print("\n🚀 Starting Comet...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print("🍪 Loading cookies...")
        load_cookies(driver, "./cookie.txt")

        print("🌐 Navigating to project...")
        project_url = "https://labs.google/fx/vi/tools/flow/project/125966c7-418b-49da-9978-49f0a62356de"
        driver.get(project_url)
        time.sleep(5)
        print("✅ Project loaded\n")

        # Fill prompt first
        print("📝 Filling prompt...")
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Tạo một video"]')
        textarea.clear()
        textarea.send_keys("A beautiful sunset over the ocean")
        time.sleep(2)
        print("✅ Prompt filled\n")

        # Find Settings button (tune icon)
        print("⚙️  Looking for Settings button (tune icon)...")
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
        settings_btn = None

        for btn in buttons:
            try:
                # Look for button with "tune" icon or "Cài đặt" aria-label
                aria_label = btn.get_attribute('aria-label')
                inner_html = btn.get_attribute('innerHTML')

                if aria_label and 'Cài đặt' in aria_label:
                    print(f"   Found Settings button by aria-label: {aria_label}")
                    settings_btn = btn
                    break
                elif 'tune' in inner_html:
                    print(f"   Found Settings button by tune icon")
                    settings_btn = btn
                    break
            except:
                pass

        if not settings_btn:
            print("❌ Settings button not found!")
            print("\n💡 Looking for x2 indicator...")
            # Try to find the x2 div
            x2_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'x2')]")
            if x2_elements:
                print(f"   Found {len(x2_elements)} elements with 'x2'")
                for elem in x2_elements:
                    print(f"   - {elem.tag_name}: {elem.text}")
            return

        print("\n🔘 Clicking Settings button...")
        settings_btn.click()
        time.sleep(2)
        print("✅ Settings dialog opened!\n")

        # Take screenshot
        from datetime import datetime
        filename = f"./comet_settings_dialog_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(filename)
        print(f"📸 Screenshot saved: {filename}\n")

        # Now look for output count setting in the dialog
        print("🔍 Looking for output count setting in dialog...")

        # Look for elements that might control the x2 setting
        # Common patterns: input, select, slider, radio buttons
        print("\n   Looking for inputs/selectors...")
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input, select, [role="slider"], [role="radiogroup"]')
        print(f"   Found {len(inputs)} interactive elements")

        for inp in inputs[:10]:  # Check first 10
            try:
                inp_type = inp.get_attribute('type')
                inp_name = inp.get_attribute('name')
                inp_aria = inp.get_attribute('aria-label')
                inp_value = inp.get_attribute('value')
                print(f"   - Type: {inp_type}, Name: {inp_name}, Aria: {inp_aria}, Value: {inp_value}")
            except:
                pass

        print("\n" + "="*80)
        print("⏸️  PAUSED - Settings dialog is open")
        print("="*80)
        print("\nYou can now:")
        print("  1. Look at Comet window - Settings dialog should be open")
        print("  2. Find the setting to change x2 to x1")
        print("  3. Check the screenshot for reference")
        print("\nCommands:")
        print("  - Press Enter to take another screenshot")
        print("  - Type 'quit' to close")
        print("="*80)

        while True:
            try:
                cmd = input("\nDebug> ").strip().lower()
                if not cmd:
                    filename = f"./comet_settings_{datetime.now().strftime('%H%M%S')}.png"
                    driver.save_screenshot(filename)
                    print(f"📸 {filename}")
                elif cmd == 'quit' or cmd == 'q':
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

if __name__ == "__main__":
    main()
