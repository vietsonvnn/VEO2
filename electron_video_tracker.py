"""
Electron-based Video Tracker for VEO Flow
Uses Playwright's Electron support for better video URL tracking
"""

import asyncio
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElectronVideoTracker:
    """
    Track video generation using Electron for precise URL mapping
    """
    
    def __init__(self, cookies_path: str):
        self.cookies_path = cookies_path
        self.page = None
        self.context = None
        self.browser = None
        self.video_map = {}  # Map: scene_number -> video_url
        
    async def start(self):
        """Start Electron browser"""
        logger.info("🚀 Starting Electron browser...")

        self.playwright = await async_playwright().start()

        # Launch Chromium with Electron-like capabilities
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            executable_path="/Applications/Comet.app/Contents/MacOS/Comet"
        )

        # Load cookies and create context with them
        with open(self.cookies_path) as f:
            cookies = json.load(f)

        self.context = await self.browser.new_context()
        await self.context.add_cookies(cookies)

        # Create page and immediately navigate to avoid about:blank issue
        self.page = await self.context.new_page()

        # Go to Flow homepage first to establish session
        logger.info("🌐 Navigating to Flow...")
        try:
            await self.page.goto("https://labs.google/fx/vi/tools/flow",
                                wait_until="domcontentloaded",
                                timeout=30000)
            await self.page.wait_for_timeout(3000)
            logger.info("✅ Electron browser started and logged in")
        except Exception as e:
            logger.error(f"❌ Error navigating to Flow: {e}")
            raise

    async def goto_flow(self):
        """Navigate to Flow (if not already there)"""
        logger.info("🌐 Going to Flow homepage...")
        await self.page.goto("https://labs.google/fx/vi/tools/flow",
                            wait_until="domcontentloaded",
                            timeout=30000)
        await self.page.wait_for_timeout(2000)
        logger.info("✅ At Flow homepage")
        
    async def goto_project(self, project_id: str):
        """Go to specific project"""
        url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
        logger.info(f"📁 Going to project: {project_id}")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(5000)  # Wait for Flow app to initialize
        logger.info("✅ Project loaded")
        
    async def track_video_creation(self, scene_number: int, prompt: str):
        """
        Track video creation with precise URL mapping
        Returns: video URL for this specific scene
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🎬 SCENE {scene_number}: {prompt[:50]}...")
        logger.info(f"{'='*60}")
        
        # Step 1: Get current video URLs (baseline)
        urls_before = await self._get_all_video_urls()
        logger.info(f"📊 Baseline: {len(urls_before)} videos on page")
        
        # Step 2: Fill prompt
        logger.info("✍️  Filling prompt...")
        await self._fill_prompt(prompt)
        
        # Step 3: Click Generate
        logger.info("🎯 Clicking Generate...")
        await self._click_generate()
        
        # Step 4: Monitor network for new video
        logger.info("👀 Monitoring for new video...")
        video_url = await self._wait_for_new_video(urls_before, timeout=120)
        
        if video_url:
            self.video_map[scene_number] = video_url
            logger.info(f"✅ Scene {scene_number} → {video_url[:80]}...")
            return video_url
        else:
            logger.error(f"❌ Scene {scene_number} failed")
            return None
            
    async def _get_all_video_urls(self):
        """Extract all Google Storage video URLs from page"""
        content = await self.page.content()
        pattern = r'https://storage\.googleapis\.com/ai-sandbox-videofx/video/[a-f0-9\-]+'
        urls = set(re.findall(pattern, content))
        return urls
        
    async def _fill_prompt(self, prompt: str):
        """Fill prompt textarea"""
        # Find textarea
        textarea = await self.page.wait_for_selector('textarea[placeholder*="prompt" i], textarea')
        
        # Clear and fill
        await textarea.click()
        await textarea.fill('')
        await self.page.wait_for_timeout(500)
        await textarea.type(prompt, delay=50)
        await self.page.wait_for_timeout(2000)
        
    async def _click_generate(self):
        """Click Generate button"""
        # Wait for button to be enabled
        button = await self.page.wait_for_selector('button:has-text("Generate"), button:has-text("Tạo")')
        
        # Wait until enabled
        for _ in range(10):
            if await button.is_enabled():
                break
            await self.page.wait_for_timeout(1000)
        
        await button.click()
        await self.page.wait_for_timeout(3000)
        
    async def _wait_for_new_video(self, urls_before: set, timeout: int = 120):
        """
        Wait for new video URL to appear
        Uses polling with network monitoring
        """
        start_time = asyncio.get_event_loop().time()
        check_interval = 3
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            elapsed = int(asyncio.get_event_loop().time() - start_time)
            logger.info(f"   ⏳ Waiting... {elapsed}s / {timeout}s")
            
            # Check for play button (video ready)
            play_button = await self.page.query_selector('button[aria-label*="Play" i], button[aria-label*="Phát" i]')
            if play_button:
                logger.info("   ✅ Play button found!")
                
                # Get new URLs
                urls_after = await self._get_all_video_urls()
                new_urls = urls_after - urls_before
                
                if new_urls:
                    # Return FIRST new URL (matches prompt best)
                    new_urls_sorted = sorted(list(new_urls))
                    logger.info(f"   📹 Found {len(new_urls)} new video(s)")
                    return new_urls_sorted[0]
                    
            await self.page.wait_for_timeout(check_interval * 1000)
            
        logger.error(f"   ⏱️ Timeout after {timeout}s")
        return None
        
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    def get_video_map(self):
        """Get complete scene -> video mapping"""
        return self.video_map


async def test_electron_tracker():
    """Test Electron video tracker"""
    
    # Test scenes
    scenes = [
        "A serene morning landscape with mountains and fog",
        "A busy city street with people walking",
        "Ocean waves crashing on a beach at sunset"
    ]
    
    tracker = ElectronVideoTracker(cookies_path="./config/cookies.json")
    
    try:
        await tracker.start()
        await tracker.goto_project("7527ed36-b1fb-4728-9cac-e42fc01698c4")
        
        # Track each scene
        for i, prompt in enumerate(scenes, 1):
            url = await tracker.track_video_creation(i, prompt)
            if not url:
                logger.error(f"Failed scene {i}")
                break
                
        # Print final mapping
        print("\n" + "="*60)
        print("📊 FINAL VIDEO MAPPING:")
        print("="*60)
        for scene_num, video_url in tracker.get_video_map().items():
            print(f"Scene {scene_num}: {video_url}")
            
        # Keep browser open
        print("\n✅ Test complete! Browser staying open...")
        print("Press Ctrl+C to close")
        await asyncio.sleep(3600)  # Keep open for 1 hour
        
    except KeyboardInterrupt:
        print("\n👋 Closing...")
    finally:
        await tracker.close()


if __name__ == "__main__":
    asyncio.run(test_electron_tracker())
