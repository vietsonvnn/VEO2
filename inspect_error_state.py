#!/usr/bin/env python3
"""
Inspect Flow page error state
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from browser_automation.flow_controller import FlowController
from datetime import datetime

async def inspect():
    """Inspect the current Flow page state"""
    controller = FlowController(cookies_path="./cookie.txt", headless=False)

    try:
        print("🚀 Starting browser...")
        await controller.start()

        print("🌐 Going to Flow project...")
        project_id = "125966c7-418b-49da-9978-49f0a62356de"
        await controller.goto_project(project_id)

        print("\n⏳ Waiting 3 seconds for page to load...")
        await asyncio.sleep(3)

        print("\n📸 Taking screenshot of current state...")
        await controller.page.screenshot(path=f"./flow_state_{datetime.now().strftime('%H%M%S')}.png")

        print("\n🔍 Inspecting page elements...")

        # Check for error messages
        print("\n1. Checking for error messages:")
        error_selectors = [
            '[role="alert"]',
            '.error',
            '.error-message',
            'div:has-text("Error")',
            'div:has-text("error")',
            'div:has-text("failed")'
        ]

        for selector in error_selectors:
            try:
                elements = await controller.page.query_selector_all(selector)
                if elements:
                    print(f"   Found {len(elements)} elements matching: {selector}")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            text = await elem.inner_text()
                            visible = await elem.is_visible()
                            print(f"      [{i}] Visible={visible}: {text[:100]}")
                        except:
                            pass
            except Exception as e:
                pass

        # Check for video player state
        print("\n2. Checking video player state:")
        video_selectors = [
            'video',
            '[role="region"]',
            '.video-container',
            'div[class*="video"]'
        ]

        for selector in video_selectors:
            try:
                elements = await controller.page.query_selector_all(selector)
                if elements:
                    print(f"   Found {len(elements)} elements matching: {selector}")
            except:
                pass

        # Check for loading states
        print("\n3. Checking loading states:")
        loading_selectors = [
            '[role="progressbar"]',
            '.loading',
            'div:has-text("Loading")',
            'div:has-text("Generating")'
        ]

        for selector in loading_selectors:
            try:
                elements = await controller.page.query_selector_all(selector)
                if elements:
                    print(f"   Found {len(elements)} elements matching: {selector}")
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = await elem.inner_text()
                            visible = await elem.is_visible()
                            print(f"      [{i}] Visible={visible}: {text[:100]}")
                        except:
                            pass
            except:
                pass

        # Check page content
        print("\n4. Getting page HTML...")
        html = await controller.page.content()

        # Save HTML for analysis
        with open(f"./flow_state_{datetime.now().strftime('%H%M%S')}.html", "w") as f:
            f.write(html)
        print("   ✅ HTML saved to flow_state_*.html")

        # Check if there are any video cards
        print("\n5. Checking for existing video cards:")
        try:
            # Look for play buttons
            play_buttons = await controller.page.query_selector_all('button:has-text("play_arrow")')
            print(f"   Found {len(play_buttons)} play buttons (videos)")

            # Look for video thumbnails
            videos = await controller.page.query_selector_all('video')
            print(f"   Found {len(videos)} video elements")

        except Exception as e:
            print(f"   Error: {e}")

        print("\n⏸️  Browser will stay open for manual inspection...")
        print("   Press Enter to close...")
        input()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await controller.close()

if __name__ == "__main__":
    asyncio.run(inspect())
