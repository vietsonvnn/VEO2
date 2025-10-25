"""
Keep Browser Open - Mở browser và giữ mở để theo dõi video generation
"""
import asyncio
from src.browser_automation import FlowController

PROJECT_ID = "559e7aca-ab4c-4f35-9076-fba5a69a18c1"

async def keep_open():
    print("="*60)
    print("KEEP BROWSER OPEN - Monitor Video Generation")
    print("="*60)
    print(f"\nProject: {PROJECT_ID}")
    print("\n⏱️  Browser sẽ mở và giữ trong 30 PHÚT")
    print("   Bạn có thể theo dõi video generation")
    print("   Press Ctrl+C để đóng sớm")
    print("="*60)

    controller = FlowController(
        cookies_path="./config/cookies.json",
        download_dir="./data/videos",
        headless=False
    )

    try:
        print("\n[1] Starting browser...")
        await controller.start()

        print("\n[2] Navigate to project...")
        await controller.goto_project(PROJECT_ID)

        print("\n[3] Browser is open!")
        print("   You can interact with the page")
        print("   Video generation will continue")
        print("\n   Keeping browser open for 30 minutes...")
        print("   (Press Ctrl+C to close early)")

        # Keep open for 30 minutes
        await asyncio.sleep(1800)

        print("\n[4] Closing browser...")
        await controller.close()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Closing browser...")
        await controller.close()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        await controller.close()

if __name__ == "__main__":
    asyncio.run(keep_open())
