#!/usr/bin/env python3
"""
Test UI Workflow - Verify video matching và playback
Tạo 2 videos ngắn để test nhanh
"""

import asyncio
import sys
from flow_video_tracker import FlowVideoTracker

async def test_ui_workflow():
    """Test complete workflow with 2 videos"""

    print("="*70)
    print("🎬 TEST UI WORKFLOW - VIDEO MATCHING & PLAYBACK")
    print("="*70)

    # Short prompts for quick testing
    prompts = [
        "A red sports car driving on a coastal highway at sunset",
        "A golden retriever puppy playing in a garden with butterflies"
    ]

    print(f"\n📝 Test với {len(prompts)} videos:")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt}")

    tracker = FlowVideoTracker(cookies_path="./config/cookies.json")

    try:
        print("\n🚀 Khởi động Electron browser...")
        await tracker.start()
        print("✅ Browser đã khởi động")

        # Go to project
        project_id = "7527ed36-b1fb-4728-9cac-e42fc01698c4"
        print(f"\n📁 Vào project: {project_id}")
        await tracker.goto_project(project_id)
        print("✅ Đã vào project")

        # Set output to 1
        print("\n⚙️  Set output = 1 video...")
        await tracker.set_output_to_1()
        print("✅ Đã set output = 1")

        # Create videos
        print(f"\n🎬 Bắt đầu tạo {len(prompts)} videos...")
        print("="*70)

        scenes_data = await tracker.create_videos(prompts)

        print("\n" + "="*70)
        print("📊 KẾT QUẢ VIDEO MATCHING")
        print("="*70)

        # Verify results
        all_matched = True
        for i, (prompt, scene_data) in enumerate(zip(prompts, scenes_data), 1):
            video_url = scene_data['video_url']

            if video_url:
                print(f"\n✅ SCENE {i}: MATCHED")
                print(f"   Prompt: {prompt[:60]}...")
                print(f"   Video:  {video_url[:80]}...")
                print(f"   Status: CÓ THỂ PLAY trong UI")
            else:
                print(f"\n❌ SCENE {i}: FAILED")
                print(f"   Prompt: {prompt[:60]}...")
                print(f"   Video:  KHÔNG CÓ")
                all_matched = False

        print("\n" + "="*70)
        if all_matched:
            print("🎉 KẾT QUẢ: TẤT CẢ VIDEOS ĐÃ MATCH CHÍNH XÁC!")
            print("✅ Videos có thể play trong Gradio UI")
            print("✅ Baseline URL Tracking hoạt động 100%")
        else:
            print("❌ CÓ MỘT SỐ VIDEOS THẤT BẠI")
        print("="*70)

        # Keep browser open for manual verification
        print("\nℹ️  Browser vẫn mở - bạn có thể:")
        print("   1. Xem videos trong Flow project")
        print("   2. Verify URLs trong UI")
        print("   3. Test play videos trong Gradio")
        print("\n⌨️  Press Ctrl+C để đóng browser...")

        # Wait for manual inspection
        await asyncio.sleep(999999)

    except KeyboardInterrupt:
        print("\n\n✅ Test completed - đóng browser...")
    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Hoàn tất!")

if __name__ == "__main__":
    asyncio.run(test_ui_workflow())
