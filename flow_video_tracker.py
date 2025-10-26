"""
Flow Video Tracker - Production version
Tạo nhiều videos và track chính xác video cho từng scene
Không đánh số vào prompt để tránh ảnh hưởng AI generation
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowVideoTracker:
    """
    Track videos using baseline URL comparison
    Không cần đánh số vào prompt, track qua before/after URLs
    """

    def __init__(self, cookies_path: str):
        self.cookies_path = cookies_path
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

        # Video mapping: scene_number -> {prompt, video_url, status}
        self.scenes: Dict[int, Dict] = {}

    async def start(self):
        """Start browser"""
        logger.info("🚀 Starting Flow Video Tracker...")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)

        with open(self.cookies_path) as f:
            cookies = json.load(f)

        # Desktop viewport
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            screen={'width': 1280, 'height': 800}
        )
        await self.context.add_cookies(cookies)
        self.page = await self.context.new_page()

        logger.info("🌐 Navigating to Flow...")
        await self.page.goto("https://labs.google/fx/vi/tools/flow",
                            wait_until="domcontentloaded",
                            timeout=30000)
        await self.page.wait_for_timeout(10000)
        logger.info("✅ Browser ready")

    async def goto_project(self, project_id: str):
        """Navigate to project"""
        url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
        logger.info(f"📁 Going to project...")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(10000)
        logger.info("✅ Project loaded")

    async def set_output_to_1(self):
        """Set output count to 1 (one-time setup)"""
        logger.info("\n⚙️  Configuring: Output count = 1...")

        # Scroll to settings
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await self.page.wait_for_timeout(2000)

        try:
            # Click Settings
            await self.page.click('button:has-text("Cài đặt")', timeout=5000)
            await self.page.wait_for_timeout(2000)

            # Find and click "2" dropdown
            elements = await self.page.query_selector_all('button, div, span')
            for elem in elements:
                text = await elem.inner_text()
                if text.strip() == "2":
                    try:
                        await elem.click()
                        await self.page.wait_for_timeout(1500)

                        # Select "1"
                        option_1 = await self.page.query_selector('[role="option"]:has-text("1"), menuitem:has-text("1")')
                        if option_1:
                            await option_1.click()
                            await self.page.wait_for_timeout(1000)
                            logger.info("   ✅ Set to 1!")
                        break
                    except:
                        continue

            # Close settings
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(1000)

        except Exception as e:
            logger.warning(f"   ⚠️  Settings error: {e}")

    async def create_videos(self, prompts: List[str]) -> Dict[int, Dict]:
        """
        Create multiple videos from prompts
        Returns: {scene_number: {prompt, video_url, status}}
        """
        total = len(prompts)
        logger.info(f"\n🎬 Creating {total} videos...")

        for i, prompt in enumerate(prompts, 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"📹 SCENE {i}/{total}")
            logger.info(f"   Prompt: {prompt[:60]}...")
            logger.info(f"{'='*70}")

            # Initialize scene info
            self.scenes[i] = {
                'prompt': prompt,
                'video_url': None,
                'status': 'pending'
            }

            # Create video
            video_url = await self._create_single_video(prompt)

            if video_url:
                self.scenes[i]['video_url'] = video_url
                self.scenes[i]['status'] = 'completed'
                logger.info(f"✅ Scene {i} completed!")
                logger.info(f"   Video: {video_url[:70]}...")
            else:
                self.scenes[i]['status'] = 'failed'
                logger.error(f"❌ Scene {i} failed!")

        return self.scenes

    async def _create_single_video(self, prompt: str) -> Optional[str]:
        """Create single video and return URL"""

        # Scroll to input area
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await self.page.wait_for_timeout(1000)

        # Get baseline URLs
        content_before = await self.page.content()
        urls_before = set(re.findall(
            r'https://storage\.googleapis\.com/ai-sandbox-videofx/video/[a-f0-9\-]+',
            content_before
        ))
        logger.info(f"   📊 Baseline: {len(urls_before)} existing videos")

        # Fill prompt (KHÔNG đánh số, giữ nguyên prompt gốc)
        logger.info("   ✍️  Filling prompt...")
        textarea = await self.page.wait_for_selector('textarea', timeout=10000)
        await textarea.click()
        await textarea.fill('')
        await self.page.wait_for_timeout(500)
        await textarea.type(prompt, delay=30)
        await self.page.wait_for_timeout(3000)

        # Click Generate (AVOID breadcrumb)
        logger.info("   🎯 Clicking Generate...")
        all_buttons = await self.page.query_selector_all('button:has-text("Tạo")')

        generate_btn = None
        for btn in all_buttons:
            inner_html = await btn.inner_html()
            inner_text = await btn.inner_text()

            # Skip breadcrumb
            if "Trình tạo cảnh" in inner_text:
                continue

            # Skip if in <ul>
            parent_tag = await btn.evaluate('el => el.parentElement?.tagName')
            if parent_tag == 'UL':
                continue

            # This is the Generate button with arrow_forward
            if "arrow_forward" in inner_html or len(inner_text.strip()) <= 5:
                generate_btn = btn
                break

        if not generate_btn:
            logger.error("   ❌ Generate button not found!")
            return None

        # Wait for enabled
        for i in range(15):
            if await generate_btn.is_enabled():
                break
            await self.page.wait_for_timeout(1000)

        await generate_btn.click()
        await self.page.wait_for_timeout(3000)
        logger.info("   ✅ Clicked Generate")

        # Wait for new video URL
        logger.info("   👀 Waiting for video...")
        video_url = await self._wait_for_new_video(urls_before, timeout=180)

        return video_url

    async def _wait_for_new_video(self, urls_before: set, timeout: int = 180) -> Optional[str]:
        """Wait for new video URL to appear"""
        start_time = asyncio.get_event_loop().time()
        check_interval = 5

        while asyncio.get_event_loop().time() - start_time < timeout:
            elapsed = int(asyncio.get_event_loop().time() - start_time)

            if elapsed % 15 == 0:  # Log every 15s
                logger.info(f"   ⏳ {elapsed}s / {timeout}s")

            # Check for new URLs
            content_after = await self.page.content()
            urls_after = set(re.findall(
                r'https://storage\.googleapis\.com/ai-sandbox-videofx/video/[a-f0-9\-]+',
                content_after
            ))

            new_urls = urls_after - urls_before
            if new_urls:
                # Return FIRST new URL
                new_urls_sorted = sorted(list(new_urls))
                logger.info(f"   ✅ Found {len(new_urls)} new video(s)!")
                return new_urls_sorted[0]

            await self.page.wait_for_timeout(check_interval * 1000)

        logger.error(f"   ⏱️ Timeout after {timeout}s")
        return None

    async def delete_video_by_url(self, video_url: str) -> bool:
        """
        Delete video by URL
        Match chính xác video với nút xoá
        """
        logger.info(f"\n🗑️  Deleting video: {video_url[:70]}...")

        # Scroll to top to see videos
        await self.page.evaluate("window.scrollTo(0, 0)")
        await self.page.wait_for_timeout(2000)

        # Step 1: Find video card containing this URL
        logger.info("   📍 Finding video card...")

        # Get all video elements
        videos = await self.page.query_selector_all('video')
        logger.info(f"   Found {len(videos)} video elements")

        target_video_card = None
        for video in videos:
            # Check if this video's src matches our URL
            src = await video.get_attribute('src')
            if src and video_url in src:
                # Found the video! Now get its parent card
                target_video_card = await video.evaluate_handle('''el => {
                    let parent = el;
                    let depth = 0;
                    while (parent && depth < 15) {
                        // Look for card container (article, section, or div with significant content)
                        if (parent.tagName === 'ARTICLE' ||
                            parent.tagName === 'SECTION' ||
                            (parent.className && parent.className.includes('card'))) {
                            return parent;
                        }
                        parent = parent.parentElement;
                        depth++;
                    }
                    return el.parentElement?.parentElement?.parentElement;
                }''')
                logger.info("   ✅ Found target video card!")
                break

        if not target_video_card:
            logger.error("   ❌ Video card not found!")
            return False

        # Step 2: Find more_vert button within this video card
        logger.info("   🔍 Finding more_vert button in video card...")

        more_btn = await target_video_card.query_selector('button[aria-haspopup="menu"]:has-text("more_vert")')

        if not more_btn:
            logger.error("   ❌ more_vert button not found!")
            return False

        logger.info("   ✅ Found more_vert button!")

        # Step 3: Click more_vert to open menu
        logger.info("   🎯 Clicking more_vert...")
        await more_btn.click(force=True)
        await self.page.wait_for_timeout(1500)
        logger.info("   ✅ Menu opened!")

        # Step 4: Find and click Delete option in menu
        logger.info("   🗑️  Finding Delete option...")

        # Wait for menu to render
        await self.page.wait_for_timeout(1000)

        # Try multiple strategies to find Delete option
        delete_option = None

        # Strategy 1: Find any visible element with exact text "Xoá"
        try:
            # Look for elements containing "Xoá" that are visible
            xoa_elements = await self.page.query_selector_all(':visible:has-text("Xoá")')

            for elem in xoa_elements:
                text = await elem.inner_text()
                # Must be exactly "Xoá" or have delete icon
                if text.strip() == "Xoá":
                    # Check if it's clickable (button, menuitem, or has click handler)
                    tag = await elem.evaluate('el => el.tagName')
                    role = await elem.get_attribute('role')

                    if tag in ['BUTTON', 'MENUITEM'] or role == 'menuitem':
                        delete_option = elem
                        logger.info(f"   ✅ Found Delete option! (tag: {tag}, role: {role})")
                        break
        except Exception as e:
            logger.warning(f"   Strategy 1 failed: {e}")

        # Strategy 2: Try menuitem selector
        if not delete_option:
            try:
                delete_option = await self.page.query_selector('menuitem:has-text("Xoá")')
                if delete_option:
                    logger.info("   ✅ Found Delete via menuitem selector!")
            except Exception as e:
                logger.warning(f"   Strategy 2 failed: {e}")

        # Strategy 3: Find by role=menuitem
        if not delete_option:
            try:
                all_menuitems = await self.page.query_selector_all('[role="menuitem"]')
                for item in all_menuitems:
                    text = await item.inner_text()
                    if "Xoá" in text:
                        delete_option = item
                        logger.info("   ✅ Found Delete via role=menuitem!")
                        break
            except Exception as e:
                logger.warning(f"   Strategy 3 failed: {e}")

        if delete_option:
            try:
                # Click delete
                await delete_option.click()
                await self.page.wait_for_timeout(2000)
                logger.info("   ✅✅ Video deleted!")
                return True
            except Exception as e:
                logger.error(f"   ❌ Failed to click Delete: {e}")
                return False
        else:
            logger.error("   ❌ Delete option not found!")

            # Debug: list all visible elements with "Xoá"
            try:
                all_xoa = await self.page.query_selector_all(':has-text("Xoá")')
                logger.info(f"   📝 Found {len(all_xoa)} elements with 'Xoá':")
                for i, item in enumerate(all_xoa[:5]):
                    text = await item.inner_text()
                    tag = await item.evaluate('el => el.tagName')
                    visible = await item.is_visible()
                    logger.info(f"      {i+1}. <{tag}> '{text[:50]}' (visible: {visible})")
            except Exception as e:
                logger.error(f"   Debug failed: {e}")

            return False

    async def delete_scene(self, scene_number: int) -> bool:
        """Delete video for specific scene"""
        if scene_number not in self.scenes:
            logger.error(f"Scene {scene_number} not found!")
            return False

        scene = self.scenes[scene_number]
        if not scene['video_url']:
            logger.error(f"Scene {scene_number} has no video URL!")
            return False

        logger.info(f"\n🗑️  Deleting Scene {scene_number}: {scene['prompt'][:50]}...")

        result = await self.delete_video_by_url(scene['video_url'])

        if result:
            # Update scene status
            scene['status'] = 'deleted'
            scene['video_url'] = None
            logger.info(f"✅ Scene {scene_number} deleted successfully!")

        return result

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def print_summary(self):
        """Print video mapping summary"""
        print("\n" + "="*70)
        print("📊 VIDEO MAPPING SUMMARY")
        print("="*70)

        completed = sum(1 for s in self.scenes.values() if s['status'] == 'completed')
        failed = sum(1 for s in self.scenes.values() if s['status'] == 'failed')

        print(f"Total: {len(self.scenes)} | ✅ Completed: {completed} | ❌ Failed: {failed}")
        print()

        for scene_num in sorted(self.scenes.keys()):
            scene = self.scenes[scene_num]
            status_icon = "✅" if scene['status'] == 'completed' else "❌"

            print(f"{status_icon} Scene {scene_num}: {scene['prompt'][:50]}...")
            if scene['video_url']:
                print(f"   → {scene['video_url']}")
            print()

        print("="*70)


async def test_multiple_scenes():
    """Test creating multiple scenes"""

    # Test với 5 scenes
    prompts = [
        "A peaceful mountain lake at sunrise with morning mist",
        "A futuristic robot walking through neon-lit city streets",
        "Colorful fireworks exploding over a beach at night",
        "A butterfly landing on a blooming flower in slow motion",
        "Ocean waves crashing on rocky cliffs during sunset"
    ]

    tracker = FlowVideoTracker(cookies_path="./config/cookies.json")

    try:
        await tracker.start()
        await tracker.goto_project("7527ed36-b1fb-4728-9cac-e42fc01698c4")
        await tracker.set_output_to_1()

        # Create all videos
        scenes = await tracker.create_videos(prompts)

        # Print summary
        tracker.print_summary()

        # Keep browser open
        print("\n✅ Test complete! Browser staying open...")
        print("Press Ctrl+C to close")
        await asyncio.sleep(3600)

    except KeyboardInterrupt:
        print("\n👋 Closing...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tracker.close()


if __name__ == "__main__":
    asyncio.run(test_multiple_scenes())
