#!/usr/bin/env python3
"""
Comet Automation - Set output count to 1
Tự động đặt "Câu trả lời đầu ra cho mỗi câu lệnh" = 1
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
    print("🎬 COMET - SET OUTPUT COUNT TO 1")
    print("="*80)

    options = Options()
    options.binary_location = "/Applications/Comet.app/Contents/MacOS/Comet"
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        print("\n🚀 Step 1: Starting Comet...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Comet started\n")

        print("🍪 Step 2: Loading cookies...")
        load_cookies(driver, "./cookie.txt")
        print("✅ Cookies loaded\n")

        print("🌐 Step 3: Navigating to project...")
        driver.get("https://labs.google/fx/vi/tools/flow/project/125966c7-418b-49da-9978-49f0a62356de")
        time.sleep(5)
        print("✅ Project loaded\n")

        print("📝 Step 4: Filling prompt...")
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Tạo một video"]')
        textarea.clear()
        time.sleep(0.5)
        textarea.send_keys(TEST_PROMPT)
        time.sleep(2)
        print(f"✅ Prompt: {TEST_PROMPT[:50]}...\n")

        print("⚙️  Step 5: Setting output count to 1...")
        print("   Looking for 'Câu trả lời đầu ra cho mỗi câu lệnh'...\n")

        # Method 1: Find button near the text "Câu trả lời đầu ra"
        try:
            # Look for text containing "Câu trả lời đầu ra"
            label_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Câu trả lời đầu ra')]")

            if label_elements:
                print(f"   ✅ Found {len(label_elements)} element(s) with text")

                # Find the button that shows current count (might be near the label)
                # Look for buttons showing numbers 1, 2, 3, or 4
                all_buttons = driver.find_elements(By.CSS_SELECTOR, 'button')

                output_count_button = None
                for btn in all_buttons:
                    try:
                        btn_text = btn.text.strip()
                        # Check if button text is a single digit (1, 2, 3, or 4)
                        if btn_text in ['1', '2', '3', '4']:
                            # Check if this button is near the label
                            print(f"   Found button with text: '{btn_text}'")
                            output_count_button = btn
                            current_value = btn_text
                            break
                    except:
                        pass

                if not output_count_button:
                    # Alternative: Look for x1, x2, x3, x4 indicator
                    print("   Trying alternative method: looking for x1/x2/x3/x4...")
                    x_elements = driver.find_elements(By.XPATH, "//*[starts-with(text(), 'x')]")
                    for elem in x_elements:
                        elem_text = elem.text.strip()
                        if elem_text in ['x1', 'x2', 'x3', 'x4']:
                            print(f"   Found indicator: {elem_text}")
                            current_value = elem_text[1]  # Get the number

                            # Try to click on this element or its parent
                            try:
                                elem.click()
                                output_count_button = elem
                                print(f"   ✅ Clicked on {elem_text}")
                                break
                            except:
                                # Try parent
                                try:
                                    parent = elem.find_element(By.XPATH, "..")
                                    parent.click()
                                    output_count_button = parent
                                    print(f"   ✅ Clicked on parent of {elem_text}")
                                    break
                                except:
                                    pass

                if output_count_button:
                    print(f"   Current value: {current_value}")

                    if current_value == '1':
                        print("   ✅ Already set to 1!\n")
                    else:
                        print(f"   Need to change from {current_value} to 1")

                        # Click to open menu
                        print("   🔘 Clicking button to open menu...")
                        if output_count_button.tag_name != 'button':
                            # If not a button, try clicking it anyway
                            try:
                                output_count_button.click()
                            except:
                                driver.execute_script("arguments[0].click();", output_count_button)
                        else:
                            output_count_button.click()

                        time.sleep(2)

                        # Take screenshot of menu
                        menu_ss = f"./comet_menu_{datetime.now().strftime('%H%M%S')}.png"
                        driver.save_screenshot(menu_ss)
                        print(f"   📸 Menu screenshot: {menu_ss}")

                        # Look for menu with class "Flow1234" or any menu items
                        print("   Looking for menu items...")

                        # Try different selectors for menu items
                        menu_selectors = [
                            '[role="menuitem"]',
                            '[role="option"]',
                            '.Flow1234 button',
                            '.Flow1234 [role="menuitem"]',
                            'button:has-text("1")'
                        ]

                        menu_items = []
                        for selector in menu_selectors:
                            try:
                                items = driver.find_elements(By.CSS_SELECTOR, selector)
                                if items:
                                    print(f"   Found {len(items)} items with selector: {selector}")
                                    menu_items.extend(items)
                                    break
                            except:
                                pass

                        if not menu_items:
                            # Try XPath to find buttons with text "1"
                            menu_items = driver.find_elements(By.XPATH, "//button[text()='1']")
                            if menu_items:
                                print(f"   Found {len(menu_items)} button(s) with text '1' via XPath")

                        # Click on "1" in menu
                        if menu_items:
                            for item in menu_items:
                                try:
                                    item_text = item.text.strip()
                                    if item_text == '1':
                                        print(f"   🔘 Clicking '1' in menu...")
                                        item.click()
                                        time.sleep(1)
                                        print("   ✅ Set to 1!\n")
                                        break
                                except Exception as e:
                                    print(f"   ⚠️  Could not click item: {e}")
                        else:
                            print("   ⚠️  No menu items found")
                            print("   Please manually change the setting\n")
                else:
                    print("   ⚠️  Could not find output count button")
            else:
                print("   ⚠️  Text 'Câu trả lời đầu ra' not found")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

        # Verify final setting
        print("\n🔍 Step 6: Verifying setting...")
        try:
            x_elements = driver.find_elements(By.XPATH, "//*[starts-with(text(), 'x')]")
            for elem in x_elements:
                elem_text = elem.text.strip()
                if elem_text in ['x1', 'x2', 'x3', 'x4']:
                    print(f"   Current setting: {elem_text}")
                    if elem_text == 'x1':
                        print("   ✅ Successfully set to x1!\n")
                    else:
                        print(f"   ⚠️  Still showing {elem_text}\n")
                    break
        except:
            pass

        # Take final screenshot
        final_ss = f"./comet_final_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(final_ss)
        print(f"📸 Final screenshot: {final_ss}\n")

        print("="*80)
        print("✅ SETUP COMPLETE")
        print("="*80)
        print("\nReady to generate video with 1 output")
        print("\nPress Enter to click Generate button...")
        input()

        # Click Generate
        print("\n🎬 Clicking Generate button...")
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
        for btn in buttons:
            try:
                if "Tạo" in btn.text and btn.is_enabled():
                    btn.click()
                    print("✅ Generate clicked!\n")

                    print("⏳ Waiting 10 seconds to see result...")
                    time.sleep(10)

                    result_ss = f"./comet_generating_{datetime.now().strftime('%H%M%S')}.png"
                    driver.save_screenshot(result_ss)
                    print(f"📸 Result: {result_ss}")
                    break
            except:
                pass

        print("\n✅ Done! Browser will stay open for 30 seconds...")
        time.sleep(30)

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
