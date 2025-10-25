"""
Google Labs Flow Browser Automation
Tự động hóa việc tạo video trên Flow với VEO 3.1
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowController:
    def __init__(
        self,
        cookies_path: str = "./config/cookies.json",
        download_dir: str = "./data/videos",
        headless: bool = False
    ):
        """
        Initialize Flow Controller

        Args:
            cookies_path: Path to cookies JSON file
            download_dir: Directory to save downloaded videos
            headless: Run browser in headless mode
        """
        self.cookies_path = cookies_path
        self.download_dir = download_dir
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        os.makedirs(download_dir, exist_ok=True)

    async def start(self):
        """Start browser and load cookies"""
        playwright = await async_playwright().start()

        logger.info("🚀 Starting browser (Chrome)...")
        # Note: Comet is not compatible with Playwright - using standard Chrome instead
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            channel='chrome',  # Use installed Chrome browser
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        # Create context with larger viewport to ensure all UI elements are visible
        # Fixed: Previous viewport was too small, causing submit button to be hidden
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # Standard Full HD resolution
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            accept_downloads=True,
            device_scale_factor=1  # Standard scaling to ensure UI elements fit
        )

        # Load cookies if exists
        if os.path.exists(self.cookies_path):
            logger.info(f"📂 Loading cookies from {self.cookies_path}")
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
                # Fix sameSite attribute - ensure it's valid
                for cookie in cookies:
                    if 'sameSite' in cookie:
                        # Normalize sameSite value
                        same_site = cookie['sameSite']
                        if same_site not in ['Strict', 'Lax', 'None']:
                            # Default to Lax if invalid
                            cookie['sameSite'] = 'Lax'
                    else:
                        # Add default sameSite if missing
                        cookie['sameSite'] = 'Lax'
                await self.context.add_cookies(cookies)
        else:
            logger.warning(f"⚠️  Cookies file not found: {self.cookies_path}")

        self.page = await self.context.new_page()
        logger.info("✅ Browser started")

    async def save_cookies(self):
        """Save current cookies to file"""
        cookies = await self.context.cookies()
        os.makedirs(os.path.dirname(self.cookies_path), exist_ok=True)

        with open(self.cookies_path, 'w') as f:
            json.dump(cookies, f, indent=2)

        logger.info(f"💾 Cookies saved to {self.cookies_path}")

    async def goto_flow(self):
        """Navigate to Flow page"""
        logger.info("🌐 Navigating to Flow...")
        await self.page.goto(
            "https://labs.google/fx/vi/tools/flow",
            wait_until="domcontentloaded",
            timeout=60000
        )
        await asyncio.sleep(5)  # Wait for dynamic content

        # Check if logged in by looking at URL (better than content check)
        try:
            page_url = self.page.url
            page_title = await self.page.title()

            logger.info(f"   Page URL: {page_url}")
            logger.info(f"   Page title: {page_title}")

            # If redirected to login page, cookies don't work
            if "accounts.google.com" in page_url or "signin" in page_url.lower():
                logger.error("❌ Redirected to login page. Cookies expired.")
                return False

            # If we're on Flow page, assume success
            if "labs.google" in page_url and "flow" in page_url.lower():
                logger.info("✅ Successfully loaded Flow (based on URL)")
                return True

        except Exception as e:
            logger.warning(f"⚠️  Login check warning: {str(e)}")

        logger.info("✅ Successfully loaded Flow")
        return True

    async def create_new_project(self, project_name: str = None) -> Optional[str]:
        """
        Create a new project in Flow by clicking "+ Dự án mới" button

        Args:
            project_name: Optional name for the project (not used, auto-generated by Flow)

        Returns:
            Project ID (UUID) if successful, None otherwise
        """
        logger.info("🆕 Creating new project...")

        try:
            # Selectors for "+ Dự án mới" button (Vietnamese UI)
            create_selectors = [
                'button:has-text("+ Dự án mới")',
                'button:has-text("Dự án mới")',
                'button:has-text("+ New Project")',
                'button:has-text("New Project")',
                # Fallback: button with "add" icon
                'button:has([class*="add"])',
                'button[aria-label*="new"]',
                'button[aria-label*="create"]',
            ]

            clicked = False
            for selector in create_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.click(selector)
                    clicked = True
                    logger.info(f"   ✅ Clicked button: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"   Selector failed: {selector}")
                    continue

            if not clicked:
                logger.error("   ❌ Could not find '+ Dự án mới' button")
                logger.info("   💡 Make sure you're on Flow dashboard page")
                logger.info("   💡 Or provide a Project ID instead")
                return None

            # Wait for navigation to new project page
            # Flow auto-generates UUID and redirects to /project/{UUID}
            logger.info("   ⏳ Waiting for redirect to new project...")
            await asyncio.sleep(5)  # Wait for page load

            # Get project ID from URL
            current_url = self.page.url
            logger.info(f"   📍 Current URL: {current_url}")

            # Extract project ID from URL (pattern: /project/{UUID})
            if "/project/" in current_url:
                project_id = current_url.split("/project/")[-1].split("?")[0].split("/")[0]
                logger.info(f"✅ New project created with ID: {project_id}")
                return project_id
            else:
                logger.warning("⚠️  Could not extract project ID from URL")
                logger.info(f"   Expected pattern: /project/{{UUID}}")
                logger.info(f"   Got: {current_url}")
                return None

        except Exception as e:
            logger.error(f"❌ Error creating project: {str(e)}")
            return None

    async def goto_project(self, project_id: str) -> bool:
        """
        Navigate to a specific project

        Args:
            project_id: The project ID

        Returns:
            True if successful
        """
        logger.info(f"📂 Navigating to project: {project_id}")

        project_url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"

        try:
            await self.page.goto(project_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            # Verify we're on the project page
            current_url = self.page.url
            if project_id in current_url:
                logger.info("✅ Successfully loaded project page")
                return True
            else:
                logger.error("❌ Failed to load project page")
                return False

        except Exception as e:
            logger.error(f"❌ Error navigating to project: {str(e)}")
            return False

    async def create_video_from_prompt(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        wait_for_generation: bool = True,
        is_first_video: bool = False
    ) -> Optional[str]:
        """
        Create video from text prompt

        Args:
            prompt: Text prompt for VEO 3.1
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1)
            wait_for_generation: Wait for video to finish generating
            is_first_video: True if this is the first video in project (needs more wait time)

        Returns:
            Video URL or None if failed
        """
        logger.info(f"🎬 Creating video with prompt: {prompt[:100]}...")

        try:
            # If first video, wait longer for page to be fully ready
            if is_first_video:
                logger.info("   ⏳ First video - waiting for page to be ready...")
                await asyncio.sleep(5)

            # Find and fill prompt textarea
            # Updated selectors based on Quytrinh.txt - node="72" is the primary selector
            prompt_selectors = [
                'textarea[node="72"]',  # PRIMARY selector from Quytrinh.txt
                'textarea[placeholder*="Tạo một video bằng văn bản"]',
                'textarea[placeholder*="Tạo một video"]',
                'textarea[placeholder*="Create a video"]',
                'textarea'
            ]

            filled = False
            max_retries = 3
            for retry in range(max_retries):
                for selector in prompt_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        # Clear any existing text first
                        await self.page.fill(selector, "")
                        await asyncio.sleep(0.5)
                        # Fill with prompt
                        await self.page.fill(selector, prompt)
                        filled = True
                        logger.info(f"✅ Prompt entered using: {selector}")
                        break
                    except Exception as e:
                        logger.debug(f"   Selector failed: {selector} - {str(e)}")
                        continue

                if filled:
                    break

                if retry < max_retries - 1:
                    logger.info(f"   ⏳ Retry {retry + 1}/{max_retries}...")
                    await asyncio.sleep(3)

            if not filled:
                logger.error("❌ Could not find prompt textarea after retries")
                # Take screenshot for debugging
                await self.page.screenshot(path=f"./debug_no_textarea_{datetime.now().strftime('%H%M%S')}.png")
                return None

            await asyncio.sleep(2)

            # Ensure "Từ văn bản sang video" is selected in scene dropdown
            # Based on Quytrinh.txt: select[node="246"]
            try:
                scene_select = await self.page.query_selector('select[node="246"]')
                if scene_select:
                    # Check current value
                    current_value = await scene_select.evaluate('el => el.value')
                    logger.info(f"   📋 Scene selector found, current value: {current_value}")

                    # Ensure it's set to "Từ văn bản sang video" mode
                    # We may need to adjust this value based on actual options
                    await self.page.select_option('select[node="246"]', index=0)
                    await asyncio.sleep(0.5)
                    logger.info("   ✅ Scene type set to video generation mode")
                else:
                    logger.debug("   ℹ️  Scene selector not found (may not be needed)")
            except Exception as e:
                logger.debug(f"   ℹ️  Could not set scene selector: {str(e)}")

            # Set aspect ratio if needed
            # This selector needs to be verified on actual Flow page
            if aspect_ratio != "16:9":
                logger.info(f"⚙️  Setting aspect ratio to {aspect_ratio}")
                # await self.page.click(f'button[data-ratio="{aspect_ratio}"]')
                # await asyncio.sleep(1)

            # Click generate button
            # Updated selectors based on Quytrinh.txt and actual Flow DOM
            generate_button_selectors = [
                'button:has-text("Tạo")',  # Primary: Text-based
                'button:has-text("arrow_forward")',  # Icon-based from Quytrinh.txt
                'button[aria-label*="Tạo"]',
                'button:has-text("Generate")',
                '[role="button"]:has-text("Tạo")',
                'button[type="submit"]'
            ]

            clicked = False
            for selector in generate_button_selectors:
                try:
                    # Wait for button to be visible and clickable
                    await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    await self.page.click(selector)
                    clicked = True
                    logger.info(f"✅ Generate button clicked: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"   Selector failed: {selector} - {str(e)}")
                    continue

            if not clicked:
                logger.error("❌ Could not find generate button")
                logger.info("   💡 You may need to click manually or update selectors")
                return None

            if not wait_for_generation:
                return "pending"

            # Wait for video generation
            logger.info("⏳ Waiting for video generation...")
            video_url = await self.wait_for_video_generation()

            return video_url

        except Exception as e:
            logger.error(f"❌ Error creating video: {str(e)}")
            return None

    async def wait_for_video_completion(self, timeout: int = 420) -> bool:
        """
        Wait for video generation to complete by checking for play button

        Args:
            timeout: Maximum wait time in seconds (default 7 minutes)

        Returns:
            True if video completed, False if timeout/failed
        """
        logger.info("⏳ Waiting for video generation to complete...")
        start_time = datetime.now()
        last_log_time = datetime.now()

        while (datetime.now() - start_time).seconds < timeout:
            try:
                # Check for play button which appears when video is ready
                # Based on Button2.txt: button with icon play_arrow
                play_button_selectors = [
                    'button:has-text("play_arrow")',
                    'button[aria-label*="play"]',
                    'button[aria-label*="Play"]',
                    '[role="button"]:has-text("play_arrow")'
                ]

                for selector in play_button_selectors:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            # IMPORTANT: Check if button is NOT disabled
                            # In SceneBuilder mode, play button exists but is disabled while loading
                            is_enabled = await element.is_enabled()

                            if is_visible and is_enabled:
                                logger.info("✅ Video generation completed! Play button is enabled.")
                                return True
                            elif is_visible and not is_enabled:
                                # Button exists but still disabled - video is still generating
                                logger.debug(f"   Play button found but disabled (still generating)...")
                    except:
                        continue

                # Log progress every 30 seconds
                elapsed = (datetime.now() - last_log_time).seconds
                if elapsed >= 30:
                    total_elapsed = (datetime.now() - start_time).seconds
                    logger.info(f"   ⏳ Still waiting... ({total_elapsed}s / {timeout}s)")
                    last_log_time = datetime.now()

                # Check for error messages
                error_selectors = ['[role="alert"]', '.error', '.error-message']
                for selector in error_selectors:
                    try:
                        error = await self.page.query_selector(selector)
                        if error:
                            error_text = await error.inner_text()
                            logger.error(f"❌ Generation error: {error_text}")
                            return False
                    except:
                        continue

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.warning(f"⚠️  Error while waiting: {str(e)}")
                await asyncio.sleep(5)

        logger.error(f"❌ Timeout after {timeout} seconds")
        return False

    async def wait_for_video_generation(self, timeout: int = 300) -> Optional[str]:
        """
        Wait for video generation to complete

        DEPRECATED: Use wait_for_video_completion() instead
        This method is kept for backwards compatibility

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            Video URL or None if timeout/failed
        """
        completed = await self.wait_for_video_completion(timeout)
        return "completed" if completed else None

    async def download_video_from_ui(
        self,
        filename: str,
        prompt_text: str = None,
        quality: str = "1080p"
    ) -> Optional[str]:
        """
        Download video using the Flow UI (more options → download → quality)

        Based on Button2.txt and downloadvideo_1.txt workflow:
        1. Find video card (optionally by prompt text)
        2. Click more options button (icon: more_vert)
        3. Click download option ("Tải xuống")
        4. Select quality option:
           - "gif" or "270p": Ảnh GIF động (270p)
           - "720p": Kích thước gốc (720p)
           - "1080p": Đã tăng độ phân giải (1080p) [DEFAULT]

        Args:
            filename: Output filename for the downloaded video
            prompt_text: Optional prompt text to identify specific video
            quality: Download quality ("gif"/"270p", "720p", or "1080p")

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            logger.info(f"📥 Downloading video from UI (quality: {quality})...")

            # Step 1: Find the more options button (icon: more_vert)
            more_options_selectors = [
                'button:has-text("more_vert")',
                'button[aria-label*="More"]',
                'button[aria-label*="options"]',
                '[role="button"]:has-text("more_vert")'
            ]

            clicked_menu = False
            for selector in more_options_selectors:
                try:
                    # If prompt_text provided, try to find the specific video card first
                    if prompt_text:
                        # Find video card containing the prompt
                        video_cards = await self.page.query_selector_all('div')
                        for card in video_cards:
                            try:
                                card_text = await card.inner_text()
                                if prompt_text.lower() in card_text.lower():
                                    # Found the card, look for more button within it
                                    more_btn = await card.query_selector(selector)
                                    if more_btn:
                                        await more_btn.click()
                                        clicked_menu = True
                                        logger.info(f"✅ Clicked more options for video: {prompt_text}")
                                        break
                            except:
                                continue
                        if clicked_menu:
                            break
                    else:
                        # Just click the first more options button
                        await self.page.wait_for_selector(selector, timeout=5000)
                        await self.page.click(selector)
                        clicked_menu = True
                        logger.info(f"✅ Clicked more options button: {selector}")
                        break
                except:
                    continue

            if not clicked_menu:
                logger.error("❌ Could not find more options button")
                return None

            # Wait for menu to appear
            await asyncio.sleep(1)

            # Step 2: Click download option ("Tải xuống")
            download_menu_selectors = [
                'button:has-text("Tải xuống")',
                '[role="menuitem"]:has-text("Tải xuống")',
                'div:has-text("Tải xuống")',
                'button:has-text("Download")',
                '[role="menuitem"]:has-text("Download")'
            ]

            clicked_download_menu = False
            for selector in download_menu_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            await element.click()
                            logger.info(f"✅ Clicked download menu: {selector}")
                            clicked_download_menu = True
                            break
                except Exception as e:
                    logger.debug(f"   Selector failed: {selector} - {str(e)}")
                    continue

            if not clicked_download_menu:
                logger.error("❌ Could not find download menu option")
                return None

            # Wait for quality options popup to appear
            await asyncio.sleep(1)

            # Step 3: Select quality option
            # Based on Giaiphap.txt: Use multiple fallback methods
            logger.info(f"   Selecting quality: {quality}")

            # Wait for menu to fully render
            try:
                await self.page.wait_for_selector('text=1080p', timeout=5000)
                logger.info("   ✅ Menu appeared with 1080p option")
            except:
                logger.warning("   ⚠️  1080p text not found, trying anyway...")

            # Try multiple methods in order (from Giaiphap.txt)
            clicked = False

            # Method 1: Click by text (simplest and most reliable)
            if not clicked:
                try:
                    await self.page.click('text=Đã tăng độ phân giải (1080p)', timeout=3000)
                    logger.info("✅ Clicked 1080p using text matching")
                    clicked = True
                except Exception as e:
                    logger.debug(f"   Text matching failed: {str(e)}")

            # Method 2: Click by icon (language-independent, recommended in Giaiphap.txt)
            if not clicked:
                try:
                    await self.page.click('text=aspect_ratio', timeout=3000)
                    logger.info("✅ Clicked 1080p using icon matching (aspect_ratio)")
                    clicked = True
                except Exception as e:
                    logger.debug(f"   Icon matching failed: {str(e)}")

            # Method 3: Position-based (3rd item in menu)
            if not clicked:
                try:
                    await self.page.locator('menu[aria-current="true"] menuitem').nth(2).click(timeout=3000)
                    logger.info("✅ Clicked 1080p using position-based selector")
                    clicked = True
                except Exception as e:
                    logger.debug(f"   Position-based failed: {str(e)}")

            # Method 4: XPath fallback
            if not clicked:
                try:
                    await self.page.locator('xpath=//*[contains(text(), "1080p")]').click(timeout=3000)
                    logger.info("✅ Clicked 1080p using XPath")
                    clicked = True
                except Exception as e:
                    logger.debug(f"   XPath failed: {str(e)}")

            if not clicked:
                logger.error("❌ All methods failed to click 1080p option")
                return None

            # Step 4: Wait for upscale if 1080p (Bước 7 trong xButton.txt)
            if quality.lower() == "1080p":
                logger.info("⏳ Waiting for 1080p upscale (this may take 1-5 minutes)...")
                await asyncio.sleep(3)

                # Wait for upscale notification to appear
                # Based on xButton.txt: li:has-text("Đang tăng độ phân giải")
                try:
                    await self.page.wait_for_selector(
                        'li:has-text("Đang tăng độ phân giải")',
                        timeout=10000
                    )
                    logger.info("   📊 Upscale process started")
                except:
                    logger.warning("   ⚠️  Upscale notification not found, continuing anyway")

                # Poll for upscale completion
                upscale_complete = False
                attempts = 0
                max_attempts = 60  # 5 minutes (60 * 5 seconds)

                while not upscale_complete and attempts < max_attempts:
                    await asyncio.sleep(5)
                    attempts += 1

                    # Check for completion notification
                    # Based on xButton.txt: li:has-text("Đã xong việc tăng độ phân giải!")
                    try:
                        # Check for completion notification (with exclamation mark!)
                        completion_notif = await self.page.query_selector('li:has-text("Đã xong việc tăng độ phân giải!")')
                        if completion_notif:
                            logger.info("✅ Upscale completed!")
                            upscale_complete = True
                            break

                        # Or check if upscaling notification disappeared
                        upscaling_notif = await self.page.query_selector('li:has-text("Đang tăng độ phân giải")')
                        if not upscaling_notif:
                            logger.info("✅ Upscale notification gone - assuming complete")
                            upscale_complete = True
                            break
                    except:
                        pass

                    # Log progress every 30 seconds
                    if attempts % 6 == 0:
                        logger.info(f"   ⏳ Still upscaling... ({attempts * 5}s / {max_attempts * 5}s)")

                if not upscale_complete:
                    logger.warning("⚠️  Upscale timeout - will try to download anyway")

                await asyncio.sleep(2)

            # Step 5: Click final download link (Bước 8 trong xButton.txt)
            # IMPORTANT: "Tải xuống" is TEXT inside <li>, NOT a button!
            # Based on xButton.txt structure:
            # <li>check_circle<br/>Đã xong việc tăng độ phân giải!<br/>Tải xuống<button>Đóng</button></li>
            logger.info("📥 Looking for final download link in notification...")

            filepath = os.path.join(self.download_dir, filename)

            try:
                # Wait a moment for notification to fully render
                await asyncio.sleep(1)

                # Setup download listener
                async with self.page.expect_download(timeout=20000) as download_info:
                    # Click on "Tải xuống" text within the completion notification
                    # Using locator to click text within the li element
                    try:
                        # Method 1: Click the text "Tải xuống" inside the success notification
                        await self.page.locator('li:has-text("Đã xong việc tăng độ phân giải!")').locator('text=Tải xuống').click()
                        logger.info("✅ Clicked download link in notification")
                    except Exception as e:
                        logger.error(f"❌ Could not click download link: {str(e)}")
                        return None

                    # Wait for download to complete
                    download = await download_info.value
                    await download.save_as(filepath)
                    logger.info(f"✅ Video saved to: {filepath}")
                    return filepath

            except Exception as e:
                # Download might have failed or timeout
                logger.error(f"❌ Download wait error: {str(e)}")

                # Check if file was downloaded anyway (browser's default download)
                # Wait a bit for potential download to finish
                await asyncio.sleep(5)

                # Check downloads folder for any new video files
                import glob
                import time

                # Check for mp4, webm, or gif files
                video_patterns = [
                    os.path.join(self.download_dir, "*.mp4"),
                    os.path.join(self.download_dir, "*.webm"),
                    os.path.join(self.download_dir, "*.gif")
                ]

                all_video_files = []
                for pattern in video_patterns:
                    all_video_files.extend(glob.glob(pattern))

                if all_video_files:
                    # Get the most recent one
                    latest_file = max(all_video_files, key=os.path.getctime)
                    file_age = os.path.getctime(latest_file)

                    # If file is very recent (within last 20 seconds), assume it's our download
                    if (time.time() - file_age) < 20:
                        # Rename it to our desired filename
                        # Keep original extension
                        orig_ext = os.path.splitext(latest_file)[1]
                        new_filepath = os.path.splitext(filepath)[0] + orig_ext

                        os.rename(latest_file, new_filepath)
                        logger.info(f"✅ Found and renamed recent download: {new_filepath}")
                        return new_filepath

                logger.error("❌ Download failed and no recent video found")
                return None

        except Exception as e:
            logger.error(f"❌ Download error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    async def download_video(self, video_url: str, filename: str) -> Optional[str]:
        """
        Download video from URL (legacy method)

        DEPRECATED: Use download_video_from_ui() for Flow videos
        This method is kept for backwards compatibility

        Args:
            video_url: Video URL
            filename: Output filename

        Returns:
            Path to downloaded file or None
        """
        try:
            logger.info(f"📥 Downloading video from URL: {video_url}")

            filepath = os.path.join(self.download_dir, filename)

            # Method 1: Use page.goto to trigger download
            async with self.page.expect_download() as download_info:
                await self.page.goto(video_url)

            download = await download_info.value
            await download.save_as(filepath)

            logger.info(f"✅ Video saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Download error: {str(e)}")
            return None

    async def generate_scene_videos(
        self,
        scenes: List[Dict],
        project_name: str = "video_project"
    ) -> List[Dict]:
        """
        Generate videos for all scenes

        Args:
            scenes: List of scene dictionaries with 'veo_prompt'
            project_name: Project name for organizing files

        Returns:
            List of scenes with video URLs and download paths
        """
        results = []

        for i, scene in enumerate(scenes, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🎬 Processing Scene {i}/{len(scenes)}")
            logger.info(f"{'='*60}")

            prompt = scene.get('veo_prompt', scene.get('description', ''))

            # Create video
            video_url = await self.create_video_from_prompt(
                prompt=prompt,
                aspect_ratio=scene.get('aspect_ratio', '16:9'),
                wait_for_generation=True
            )

            scene_result = {
                **scene,
                'video_url': video_url,
                'download_path': None,
                'status': 'success' if video_url else 'failed'
            }

            if video_url and video_url != "pending":
                # Download video
                filename = f"{project_name}_scene_{i:03d}.mp4"
                download_path = await self.download_video(video_url, filename)
                scene_result['download_path'] = download_path

            results.append(scene_result)

            # Small delay between scenes
            if i < len(scenes):
                logger.info("⏳ Waiting 10 seconds before next scene...")
                await asyncio.sleep(10)

        return results

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("👋 Browser closed")


# Example usage
async def main():
    controller = FlowController(headless=False)

    try:
        await controller.start()
        await controller.goto_flow()

        # Save cookies after successful login
        await controller.save_cookies()

        # Test single video creation
        test_prompt = """
        A cinematic shot of a lush Amazon rainforest canopy at golden hour.
        The camera slowly pans right across the dense green foliage as rays of
        warm sunlight pierce through the mist. Birds fly across the frame.
        Peaceful and serene atmosphere with soft ambient lighting.
        """

        video_url = await controller.create_video_from_prompt(test_prompt)

        if video_url:
            print(f"✅ Video created: {video_url}")
        else:
            print("❌ Failed to create video")

    finally:
        await controller.close()


if __name__ == "__main__":
    asyncio.run(main())
