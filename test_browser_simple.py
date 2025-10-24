"""Simple browser test - Windows compatible"""
import asyncio
from src.browser_automation import FlowController

async def test():
    print("="*60)
    print("BROWSER TEST - Checking Flow Access")
    print("="*60)

    controller = FlowController(
        cookies_path="./config/cookies.json",
        headless=False  # Show browser
    )

    try:
        print("\n[1] Starting browser...")
        await controller.start()
        print("    OK: Browser started")

        print("\n[2] Loading Flow...")
        success = await controller.goto_flow()

        if success:
            print("    OK: Flow loaded")
            print("\n" + "="*60)
            print("CHECK BROWSER WINDOW:")
            print("- Do you see Flow interface?")
            print("- Are you logged in?")
            print("="*60)

            input("\nPress Enter when done checking...")

            await controller.save_cookies()
            print("\nCookies saved!")

        else:
            print("    FAIL: Cannot access Flow")
            print("\nPossible issues:")
            print("1. Cookies expired - need to extract new ones")
            print("2. Network issue")
            print("3. Flow URL changed")

        print("\n[3] Closing browser...")
        await controller.close()
        print("    OK: Done")

        print("\n" + "="*60)
        if success:
            print("RESULT: SUCCESS - Ready for video generation!")
        else:
            print("RESULT: FAILED - Fix cookies first")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        await controller.close()

if __name__ == "__main__":
    asyncio.run(test())
