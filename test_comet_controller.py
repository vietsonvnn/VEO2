#!/usr/bin/env python3
"""
Test the Selenium-based FlowController with Comet
Quick test to verify Comet integration works
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from browser_automation.flow_controller_selenium import FlowControllerSelenium

def test_comet_controller():
    print("="*80)
    print("🧪 TESTING COMET CONTROLLER (SELENIUM)")
    print("="*80)
    print()

    print("📋 Test Plan:")
    print("  1. Start Comet browser")
    print("  2. Load cookies")
    print("  3. Navigate to Flow")
    print("  4. Navigate to project")
    print("  5. Take screenshot")
    print("  6. Pause for inspection")
    print("  7. Close browser")
    print()

    controller = None

    try:
        # Step 1: Start browser
        print("🚀 Step 1: Starting Comet browser...")
        print("-" * 80)
        controller = FlowControllerSelenium(
            cookies_path="./cookie.txt",
            headless=False
        )
        controller.start()
        print()

        # Step 2: Navigate to Flow
        print("🌐 Step 2: Navigating to Flow...")
        print("-" * 80)
        controller.goto_flow()
        print()

        # Step 3: Navigate to project
        print("📁 Step 3: Navigating to project...")
        print("-" * 80)
        project_id = "125966c7-418b-49da-9978-49f0a62356de"
        success = controller.goto_project(project_id)
        print()

        if success:
            print("✅ Successfully loaded project!")
        else:
            print("⚠️  Project loading may have issues")

        # Step 4: Screenshot
        print("📸 Step 4: Taking screenshot...")
        print("-" * 80)
        controller.save_screenshot("./test_comet_controller.png")
        print()

        # Step 5: Pause
        print("="*80)
        print("⏸️  PAUSED FOR INSPECTION")
        print("="*80)
        print()
        print("🔍 Comet browser is now open!")
        print()
        print("Current state:")
        print(f"  - URL: {controller.driver.current_url}")
        print(f"  - Title: {controller.driver.title}")
        print()
        print("Commands:")
        print("  - Press Enter to close browser")
        print("  - Type 'screenshot' to take another screenshot")
        print("  - Type 'quit' to exit")
        print()
        print("="*80)

        # Interactive loop
        while True:
            try:
                cmd = input("\nTest> ").strip().lower()

                if not cmd or cmd == "quit" or cmd == "q":
                    print("\n👋 Closing browser...")
                    break

                elif cmd == "screenshot" or cmd == "ss":
                    from datetime import datetime
                    filename = f"./test_comet_{datetime.now().strftime('%H%M%S')}.png"
                    controller.save_screenshot(filename)
                    print(f"📸 Screenshot saved: {filename}")

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
        if controller:
            controller.close()
        print("\n✅ Test completed!")
        print("="*80)

if __name__ == "__main__":
    print()
    test_comet_controller()
