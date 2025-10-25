#!/usr/bin/env python3
"""
Test clicking on x2 to see if it opens a menu/dialog
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

def load_cookies(driver, cookie_file):
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
    print("🧪 TEST: Click on x2 element")
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
        driver.get("https://labs.google/fx/vi/tools/flow/project/125966c7-418b-49da-9978-49f0a62356de")
        time.sleep(5)
        print("✅ Project loaded\n")

        print("📝 Filling prompt...")
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Tạo một video"]')
        textarea.clear()
        textarea.send_keys("Test prompt")
        time.sleep(2)
        print("✅ Prompt filled\n")

        # Find x2 element
        print("🔍 Looking for x2 element...")
        x2_element = None

        # Try XPath
        try:
            x2_element = driver.find_element(By.XPATH, "//*[text()='x2']")
            print(f"✅ Found x2 element!")
            print(f"   Tag: {x2_element.tag_name}")
            print(f"   Class: {x2_element.get_attribute('class')}")
            print(f"   Clickable: {x2_element.is_enabled()}")
            print(f"   Visible: {x2_element.is_displayed()}")
        except Exception as e:
            print(f"❌ Could not find x2: {e}")
            return

        # Take screenshot before click
        before = f"./x2_before_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(before)
        print(f"\n📸 Before: {before}")

        # Try to click on x2
        print("\n🔘 Attempting to click x2...")
        try:
            x2_element.click()
            time.sleep(2)
            print("✅ Clicked x2!")
        except Exception as e:
            print(f"⚠️  Direct click failed: {e}")
            print("   Trying JavaScript click...")
            try:
                driver.execute_script("arguments[0].click();", x2_element)
                time.sleep(2)
                print("✅ JavaScript click succeeded!")
            except Exception as e2:
                print(f"❌ JavaScript click also failed: {e2}")

        # Take screenshot after click
        after = f"./x2_after_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(after)
        print(f"📸 After: {after}")

        # Check if anything opened
        print("\n🔍 Checking if dialog/menu opened...")

        # Look for dialog/modal
        dialogs = driver.find_elements(By.CSS_SELECTOR, '[role="dialog"], [role="menu"], .modal')
        if dialogs:
            print(f"✅ Found {len(dialogs)} dialog(s)/menu(s)!")
            for i, dialog in enumerate(dialogs):
                if dialog.is_displayed():
                    print(f"   Dialog {i}: visible=True")
        else:
            print("❌ No dialog/menu found")

        # Also check the parent/sibling elements of x2
        print("\n🔍 Checking parent/container of x2...")
        try:
            parent = x2_element.find_element(By.XPATH, "..")
            print(f"   Parent tag: {parent.tag_name}")
            print(f"   Parent class: {parent.get_attribute('class')}")

            # Try clicking parent
            print("\n🔘 Trying to click parent element...")
            parent.click()
            time.sleep(2)

            after2 = f"./x2_parent_click_{datetime.now().strftime('%H%M%S')}.png"
            driver.save_screenshot(after2)
            print(f"📸 After parent click: {after2}")

        except Exception as e:
            print(f"⚠️  Could not interact with parent: {e}")

        print("\n" + "="*80)
        print("⏸️  PAUSED - Check Comet window")
        print("="*80)
        print("\nPress Enter to close...")
        input()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
