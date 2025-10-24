"""
Test video generation với Flow
Script này sẽ test browser automation
"""

import asyncio
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.browser_automation import FlowController

async def test_browser_access():
    """Test browser có thể access Flow không"""
    print("="*60)
    print("TEST 1: Browser Access to Flow")
    print("="*60)

    controller = FlowController(
        cookies_path="./config/cookies.json",
        download_dir="./data/videos",
        headless=False  # Show browser để bạn xem
    )

    try:
        print("\n1. Starting browser...")
        await controller.start()
        print("   ✅ Browser started")

        print("\n2. Loading cookies...")
        # Cookies đã load trong start()
        print("   ✅ Cookies loaded")

        print("\n3. Navigating to Flow...")
        success = await controller.goto_flow()

        if success:
            print("   ✅ Successfully accessed Flow!")
            print("\n" + "="*60)
            print("CHECK THE BROWSER:")
            print("- Bạn có thấy trang Flow không?")
            print("- Bạn đã đăng nhập chưa?")
            print("="*60)

            input("\nPress Enter khi đã kiểm tra xong...")

            # Save cookies for future
            await controller.save_cookies()
            print("\n✅ Cookies saved")

        else:
            print("   ❌ Failed to access Flow")
            print("\n   Possible issues:")
            print("   - Cookies expired (cần extract lại)")
            print("   - Network issue")
            print("   - Flow URL changed")

        print("\n4. Closing browser...")
        await controller.close()
        print("   ✅ Browser closed")

        return success

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        await controller.close()
        return False


async def test_single_video_generation():
    """Test tạo 1 video đơn giản"""
    print("\n" + "="*60)
    print("TEST 2: Generate Single Video")
    print("="*60)

    # Simple prompt
    test_prompt = """
    A cinematic wide shot of a peaceful forest at golden hour.
    Sunlight filters through tall trees creating dramatic rays of light.
    The camera slowly pans right revealing the depth of the forest.
    Soft, warm lighting with rich greens and golden tones.
    Serene and peaceful atmosphere. 4K quality.
    """

    controller = FlowController(
        cookies_path="./config/cookies.json",
        download_dir="./data/videos",
        headless=False
    )

    try:
        print("\n1. Starting browser...")
        await controller.start()

        print("\n2. Navigating to Flow...")
        success = await controller.goto_flow()

        if not success:
            print("❌ Cannot access Flow")
            await controller.close()
            return False

        print("\n3. Creating video...")
        print(f"   Prompt: {test_prompt[:100]}...")

        print("\n⚠️  IMPORTANT:")
        print("   - This will use 1 video from your Flow quota")
        print("   - Generation takes 5-7 minutes")
        print("   - Browser will stay open so you can watch")

        confirm = input("\nContinue? (y/n): ")
        if confirm.lower() != 'y':
            print("\nCancelled.")
            await controller.close()
            return False

        # Create video
        video_url = await controller.create_video_from_prompt(
            prompt=test_prompt,
            wait_for_generation=True
        )

        if video_url and video_url != "pending":
            print(f"\n✅ Video created!")
            print(f"   URL: {video_url}")

            # Download
            print("\n4. Downloading video...")
            download_path = await controller.download_video(
                video_url,
                "test_video.mp4"
            )

            if download_path:
                print(f"   ✅ Downloaded: {download_path}")
            else:
                print("   ⚠️  Download failed, but video URL available")
        else:
            print("\n❌ Video generation failed")
            print("   Check browser for errors")

        print("\n5. Closing browser...")
        await controller.close()

        return video_url is not None

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        await controller.close()
        return False


async def main():
    """Main test function"""
    print("="*60)
    print("VEO VIDEO GENERATION TEST")
    print("="*60)

    print("\nWhat do you want to test?")
    print("1. Browser Access Only (quick, no quota used)")
    print("2. Full Video Generation (uses 1 quota, ~5-7 min)")
    print("3. Both")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        await test_browser_access()
    elif choice == "2":
        await test_single_video_generation()
    elif choice == "3":
        success1 = await test_browser_access()
        if success1:
            print("\n" + "="*60)
            print("Browser test passed! Continuing to video generation...")
            print("="*60)
            await asyncio.sleep(2)
            await test_single_video_generation()
        else:
            print("\n❌ Browser test failed. Fix cookies first.")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
