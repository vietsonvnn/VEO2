"""
Cookie Extraction Tool
Trích xuất cookies từ trình duyệt để sử dụng trong automation

Cách dùng:
1. Cài extension "Cookie Editor" hoặc "EditThisCookie"
2. Đăng nhập vào https://labs.google/fx/vi/tools/flow
3. Export cookies dưới dạng JSON
4. Chạy script này để convert sang format của Playwright
"""

import json
import os


def convert_cookie_editor_format(input_file: str, output_file: str = "./config/cookies.json"):
    """
    Convert Cookie Editor format to Playwright format

    Args:
        input_file: Path to exported cookies JSON
        output_file: Output path for converted cookies
    """
    print(f"📂 Reading cookies from: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        cookies = json.load(f)

    # Convert to Playwright format
    playwright_cookies = []

    for cookie in cookies:
        # Handle sameSite - convert null to Lax
        same_site = cookie.get('sameSite')
        if same_site is None or same_site == 'null' or same_site not in ['Strict', 'Lax', 'None']:
            same_site = 'Lax'

        playwright_cookie = {
            'name': cookie.get('name', ''),
            'value': cookie.get('value', ''),
            'domain': cookie.get('domain', '.google.com'),
            'path': cookie.get('path', '/'),
            'expires': cookie.get('expirationDate', -1),
            'httpOnly': cookie.get('httpOnly', False),
            'secure': cookie.get('secure', False),
            'sameSite': same_site
        }

        # Remove expires if it's -1 (session cookie)
        if playwright_cookie['expires'] == -1:
            playwright_cookie.pop('expires', None)

        playwright_cookies.append(playwright_cookie)

    # Save to output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(playwright_cookies, f, indent=2)

    print(f"✅ Cookies converted and saved to: {output_file}")
    print(f"📊 Total cookies: {len(playwright_cookies)}")

    # Show important cookies
    important_cookies = [c['name'] for c in playwright_cookies if 'SID' in c['name'] or 'SSID' in c['name']]
    if important_cookies:
        print(f"🔑 Important auth cookies found: {', '.join(important_cookies)}")
    else:
        print("⚠️  Warning: No authentication cookies found (SID, SSID)")


def manual_cookie_input():
    """Manual cookie input guide"""
    print("\n" + "="*60)
    print("📋 HƯỚNG DẪN TRÍCH XUẤT COOKIES")
    print("="*60)
    print("""
1. Cài đặt extension "Cookie Editor" hoặc "EditThisCookie"
   - Chrome: https://chrome.google.com/webstore
   - Edge: https://microsoftedge.microsoft.com/addons

2. Đăng nhập vào Flow:
   https://labs.google/fx/vi/tools/flow

3. Click vào icon extension Cookie Editor

4. Click nút "Export" → "Export as JSON"

5. Lưu file JSON (ví dụ: cookies_raw.json)

6. Chạy lệnh:
   python tools/extract_cookies.py cookies_raw.json

Hoặc nếu bạn đã có cookies dạng JSON array:
   python tools/extract_cookies.py --file cookies_raw.json
""")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        manual_cookie_input()
        print("\n💡 Usage: python tools/extract_cookies.py <cookie_file.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)

    try:
        convert_cookie_editor_format(input_file)
        print("\n✅ Done! You can now run the automation.")
        print("   Test with: python main.py --topic 'Your video topic'")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
