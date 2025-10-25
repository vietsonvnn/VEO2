"""
Google Labs Flow Browser Automation with Selenium + Comet
Tự động hóa việc tạo video trên Flow với VEO 3.1 sử dụng Comet browser
"""

import time
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowControllerSelenium:
    """Flow Controller using Selenium with Comet browser"""

    def __init__(
        self,
        cookies_path: str = "./cookie.txt",
        download_dir: str = "./data/videos",
        headless: bool = False
    ):
        """
        Initialize Flow Controller with Selenium + Comet

        Args:
            cookies_path: Path to cookies JSON file
            download_dir: Directory to save downloaded videos
            headless: Run browser in headless mode (False for Comet visibility)
        """
        self.cookies_path = cookies_path
        self.download_dir = download_dir
        self.headless = headless
        self.driver = None

        os.makedirs(download_dir, exist_ok=True)

    def start(self):
        """Start Comet browser and load cookies"""
        logger.info("🚀 Starting Comet browser...")

        # Configure Comet
        options = Options()
        options.binary_location = "/Applications/Comet.app/Contents/MacOS/Comet"

        # Add arguments for better automation
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if self.headless:
            options.add_argument('--headless')

        # Use webdriver-manager to auto-download correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        logger.info("✅ Comet browser started")

        # Load cookies
        self._load_cookies()

    def _load_cookies(self):
        """Load cookies from JSON file"""
        if not os.path.exists(self.cookies_path):
            logger.warning(f"⚠️  Cookie file not found: {self.cookies_path}")
            return

        logger.info(f"📂 Loading cookies from {self.cookies_path}")

        with open(self.cookies_path, 'r') as f:
            cookies = json.load(f)

        # First navigate to the domain
        self.driver.get("https://labs.google")
        time.sleep(2)

        # Add cookies
        for cookie in cookies:
            selenium_cookie = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie.get('path', '/'),
            }

            # Optional fields
            if 'expiry' in cookie:
                selenium_cookie['expiry'] = int(cookie['expiry'])
            if 'secure' in cookie:
                selenium_cookie['secure'] = cookie['secure']
            if 'httpOnly' in cookie:
                selenium_cookie['httpOnly'] = cookie['httpOnly']
            if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
                selenium_cookie['sameSite'] = cookie['sameSite']

            try:
                self.driver.add_cookie(selenium_cookie)
            except Exception as e:
                logger.debug(f"   Could not add cookie {cookie['name']}: {e}")

        logger.info("✅ Cookies loaded")

    def goto_flow(self):
        """Navigate to Flow homepage"""
        logger.info("🌐 Navigating to Flow...")
        self.driver.get("https://labs.google/fx/vi/tools/flow")
        time.sleep(3)
        logger.info(f"✅ Navigated to Flow: {self.driver.current_url}")

    def goto_project(self, project_id: str) -> bool:
        """Navigate to specific project"""
        logger.info(f"📁 Navigating to project: {project_id}")
        project_url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
        self.driver.get(project_url)
        time.sleep(5)  # Wait for page to load

        # Check if we successfully loaded the project
        if "project" in self.driver.current_url:
            logger.info("✅ Project loaded successfully")
            return True
        else:
            logger.error("❌ Failed to load project")
            return False

    def create_new_project(self, title: str) -> Optional[str]:
        """Create a new project (placeholder - not fully implemented)"""
        logger.warning("⚠️  Project creation not implemented in Selenium version")
        return None

    def create_video_from_prompt(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        is_first_video: bool = False,
        progress_callback=None
    ) -> Optional[str]:
        """
        Create a video from text prompt

        Args:
            prompt: Text prompt for video generation
            aspect_ratio: Aspect ratio (default "16:9")
            is_first_video: Whether this is the first video in the project

        Returns:
            Video URL if successful, None otherwise
        """
        logger.info(f"🎬 Creating video from prompt...")
        logger.info(f"   Prompt: {prompt[:50]}...")

        try:
            # Step 0: Check queue limit (Flow allows max 5 pending videos)
            logger.info("   📊 Checking Flow queue...")
            queue_ready = self._wait_for_queue_slot(max_wait=300)  # Wait up to 5 minutes
            if not queue_ready:
                logger.error("   ❌ Queue is full and timeout waiting for slot")
                return None

            # Step 1: Find textarea
            logger.info("   🔍 Finding textarea...")
            textarea = self._find_textarea()
            if not textarea:
                logger.error("   ❌ Textarea not found")
                return None

            # Step 2: Fill prompt
            logger.info("   📝 Filling prompt...")
            textarea.clear()
            textarea.send_keys(prompt)
            time.sleep(2)
            logger.info("   ✅ Prompt filled")

            # Step 3: Find and click Generate button
            logger.info("   🎬 Looking for Generate button...")
            generate_button = self._find_generate_button()
            if not generate_button:
                logger.error("   ❌ Generate button not found")
                return None

            if not generate_button.is_enabled():
                logger.warning("   ⚠️  Generate button not enabled yet, waiting...")
                time.sleep(2)

            logger.info("   🎬 Clicking Generate button...")
            generate_button.click()
            time.sleep(2)
            logger.info("   ✅ Generate button clicked")

            # Step 4: Wait for video generation to complete
            logger.info("   ⏳ Waiting for video generation...")
            success = self._wait_for_video_generation(progress_callback=progress_callback)

            if success:
                logger.info("   ✅ Video generation completed!")

                # Extract video URL from page
                video_url = self._extract_video_url()

                if video_url:
                    logger.info(f"   🎬 Video URL extracted: {video_url[:80]}...")
                    return video_url
                else:
                    logger.warning("   ⚠️  Could not extract video URL, returning placeholder")
                    return f"https://labs.google/fx/vi/tools/flow/video/generated"
            else:
                logger.error("   ❌ Video generation failed or timed out")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error creating video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _wait_for_queue_slot(self, max_wait: int = 300) -> bool:
        """
        Wait for available slot in Flow queue
        Flow limits: Max 5 videos pending at once

        Args:
            max_wait: Maximum wait time in seconds (default 5 minutes)

        Returns:
            True if slot available, False if timeout
        """
        logger.info("   🔍 Checking Flow queue status...")

        start_time = time.time()
        check_interval = 10  # Check every 10 seconds

        while time.time() - start_time < max_wait:
            elapsed = int(time.time() - start_time)

            # Count pending videos in queue
            pending_count = self._count_pending_videos()

            logger.info(f"      📊 Queue status: {pending_count}/5 pending videos")

            if pending_count < 5:
                logger.info(f"      ✅ Queue has space ({pending_count}/5) - Can submit new video")
                return True
            else:
                remaining = max_wait - elapsed
                logger.info(f"      ⏳ Queue full (5/5) - Waiting... ({remaining}s remaining)")
                time.sleep(check_interval)

        logger.error(f"      ⏱️ Timeout after {max_wait}s - Queue still full")
        return False

    def _count_pending_videos(self) -> int:
        """
        Count number of videos currently pending/generating in Flow queue

        Returns:
            Number of pending videos (0-5)
        """
        try:
            # Method 1: Count progress bars with % (indicates generating)
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text

            import re
            # Find all percentages (indicates videos in progress)
            percent_matches = re.findall(r'\b(\d{1,3})%\b', body_text)

            # Each unique percentage likely represents one video
            # But this is rough - count visible progress indicators
            pending_count = len(percent_matches)

            # Method 2: Look for "Generating..." text occurrences
            generating_count = body_text.lower().count('generating')
            if generating_count > 0:
                pending_count = max(pending_count, generating_count)

            # Method 3: Count video elements that are still loading
            video_elements = self.driver.find_elements(By.TAG_NAME, 'video')
            loading_videos = 0
            for video in video_elements:
                try:
                    # Check if video has duration (loaded) or not (loading)
                    duration = video.get_attribute('duration')
                    if not duration or duration == '0':
                        loading_videos += 1
                except:
                    pass

            pending_count = max(pending_count, loading_videos)

            # Clamp between 0-5
            pending_count = min(max(pending_count, 0), 5)

            return pending_count

        except Exception as e:
            logger.debug(f"      Could not count pending videos: {e}")
            # If can't determine, assume safe (return 0 to allow submission)
            return 0

    def _find_textarea(self) -> Optional[any]:
        """Find the prompt input textarea"""
        textarea_selectors = [
            'textarea[placeholder*="Tạo một video bằng văn bản"]',
            'textarea[placeholder*="Tạo một video"]',
            'textarea[node="72"]',
            'textarea'
        ]

        for selector in textarea_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    logger.info(f"      Found textarea: {selector}")
                    return elements[0]
            except:
                pass

        return None

    def _find_generate_button(self) -> Optional[any]:
        """Find the Generate button"""
        # Look for button with "Tạo" text
        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button')

        for btn in all_buttons:
            try:
                text = btn.text
                if "Tạo" in text and btn.is_displayed():
                    logger.info(f"      Found Generate button")
                    return btn
            except:
                pass

        return None

    def _wait_for_video_generation(self, timeout: int = 120, progress_callback=None) -> bool:
        """
        Wait for video generation to complete with real-time progress tracking

        Args:
            timeout: Maximum wait time in seconds
            progress_callback: Optional callback function(elapsed, percent, screenshot_path)

        Returns:
            True if video generated successfully, False otherwise
        """
        logger.info(f"      Waiting up to {timeout}s for generation...")

        start_time = time.time()
        check_interval = 3  # Check every 3 seconds for more frequent updates
        last_screenshot_time = 0
        screenshot_interval = 10  # Take screenshot every 10 seconds

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            percent = int((elapsed / timeout) * 100)

            logger.info(f"      ⏳ Progress: {percent}% ({elapsed}s / {timeout}s)")

            # Take periodic screenshots
            screenshot_path = None
            if time.time() - last_screenshot_time >= screenshot_interval:
                try:
                    from datetime import datetime
                    screenshot_path = f"./data/logs/progress_{datetime.now().strftime('%H%M%S')}.png"
                    os.makedirs("./data/logs", exist_ok=True)
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"      📸 Screenshot saved: {screenshot_path}")
                    last_screenshot_time = time.time()
                except Exception as e:
                    logger.debug(f"      Screenshot failed: {e}")

            # Call progress callback if provided
            if progress_callback:
                try:
                    progress_callback(elapsed, percent, screenshot_path)
                except Exception as e:
                    logger.debug(f"      Progress callback failed: {e}")

            # Check for progress bar on page
            progress_info = self._check_generation_progress()
            if progress_info:
                logger.info(f"      🎬 Flow progress: {progress_info}")

            # Look for play button (indicates video is ready)
            play_button = self._find_play_button()
            if play_button:
                logger.info("      ✅ Play button found - video ready!")
                # Take final screenshot
                try:
                    from datetime import datetime
                    final_screenshot = f"./data/logs/completed_{datetime.now().strftime('%H%M%S')}.png"
                    self.driver.save_screenshot(final_screenshot)
                    logger.info(f"      📸 Final screenshot: {final_screenshot}")
                except:
                    pass
                return True

            # Look for error indicators
            if self._check_for_errors():
                logger.error("      ❌ Error detected during generation")
                return False

            time.sleep(check_interval)

        logger.error(f"      ⏱️ Timeout after {timeout}s")
        return False

    def _find_play_button(self) -> Optional[any]:
        """
        Find the play button (indicates video is ready)
        Also checks for video completion indicators
        """
        # Method 1: Look for play_arrow icon (Flow's video player)
        try:
            # Find elements containing "play_arrow" text (Material icon)
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # Check if play_arrow icon exists AND progress % is gone
            if "play_arrow" in body_text:
                # Verify video is ready by checking no progress %
                import re
                percent_matches = re.findall(r'\b(\d{1,3})%\b', body_text)
                if not percent_matches:  # No % means video complete
                    logger.info(f"      ✅ Found play_arrow icon and no progress %")
                    return True
        except:
            pass

        # Method 2: Look for video duration "0:08" (8 seconds video)
        try:
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            # Pattern for video duration: 0:08, 0:07, etc.
            import re
            duration_matches = re.findall(r'0:\d{2}', body_text)
            if duration_matches:
                logger.info(f"      ✅ Found video duration: {duration_matches[0]}")
                return True
        except:
            pass

        # Method 3: Traditional play button selectors
        play_button_selectors = [
            'button[aria-label*="Play"]',
            'button[aria-label*="play"]',
            'button.play-button',
            '[role="button"][aria-label*="Play"]'
        ]

        for selector in play_button_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        logger.info(f"      ✅ Found play button via selector: {selector}")
                        return element
            except:
                pass

        return None

    def _check_generation_progress(self) -> Optional[str]:
        """
        Check for progress indicators on the Flow page
        Based on Flow's actual progress display: 3%, 9%, 15%, 21%, 33%, 45%, 57%...

        Returns:
            Progress string if found, None otherwise
        """
        try:
            # Look for progress percentage text (e.g., "3%", "9%", "15%", "45%")
            # Flow shows: 3% → 9% → 15% → 21% → 33% → 45% → 57% → ... → 100%
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # Check for percentage patterns (1-3 digits + %)
            import re
            percent_matches = re.findall(r'\b(\d{1,3})%\b', body_text)
            if percent_matches:
                # Get all percentages found
                percentages = [int(p) for p in percent_matches if int(p) <= 100]
                if percentages:
                    # Return the highest percentage (most recent progress)
                    max_percent = max(percentages)
                    return f"{max_percent}%"

            # Check for "Generating..." or similar text
            if "generating" in body_text.lower() or "đang tạo" in body_text.lower():
                return "Generating..."

            # Check for model name "Veo 3.1 - Fast" (indicates video in progress)
            if "Veo 3.1" in body_text and "Fast" in body_text:
                return "Processing (Veo 3.1 Fast)"

            # Check for progress bar elements
            progress_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="progressbar"]')
            if progress_elements:
                for elem in progress_elements:
                    aria_valuenow = elem.get_attribute('aria-valuenow')
                    if aria_valuenow:
                        return f"{aria_valuenow}%"

        except Exception as e:
            logger.debug(f"      Could not check progress: {e}")

        return None

    def _check_for_errors(self) -> bool:
        """
        Check if there are any error messages on the page
        Flow shows "Không tạo được" when video generation fails
        """
        # Flow-specific error message
        error_keywords = [
            "không tạo được",  # Flow's Vietnamese error message
            "failed to generate",
            "error",
            "failed",
            "lỗi",
            "thất bại"
        ]

        try:
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            for keyword in error_keywords:
                if keyword in body_text:
                    logger.error(f"      ❌ Error detected: '{keyword}' found on page")
                    return True
        except:
            pass

        return False

    def _extract_video_url(self) -> Optional[str]:
        """
        Extract video URL from Flow page after video generation completes
        Methods:
        1. Get <video> src attribute
        2. Convert blob URL to downloadable URL if needed
        3. Extract Google Storage URL from network
        """
        try:
            # Method 1: Find <video> element and get src
            video_elements = self.driver.find_elements(By.TAG_NAME, 'video')

            for video in video_elements:
                if video.is_displayed():
                    src = video.get_attribute('src')
                    if src:
                        logger.info(f"      Found video src: {src[:80]}...")

                        # If blob URL, try to convert to actual URL
                        if src.startswith('blob:'):
                            logger.info("      Blob URL detected, attempting to extract actual URL...")
                            actual_url = self._convert_blob_to_url(src)
                            if actual_url:
                                return actual_url
                            # If can't convert, download blob and save locally
                            else:
                                local_path = self._download_blob_video(src)
                                if local_path:
                                    return local_path
                        else:
                            # Direct URL (Google Storage or similar)
                            return src

            # Method 2: Check for source elements
            source_elements = self.driver.find_elements(By.CSS_SELECTOR, 'video source')
            for source in source_elements:
                src = source.get_attribute('src')
                if src:
                    logger.info(f"      Found source src: {src[:80]}...")
                    return src

            logger.warning("      No video URL found on page")
            return None

        except Exception as e:
            logger.error(f"      Error extracting video URL: {e}")
            return None

    def _convert_blob_to_url(self, blob_url: str) -> Optional[str]:
        """
        Try to find the actual URL behind a blob URL
        Check network requests for Google Storage URLs
        """
        try:
            # Execute JavaScript to get blob content
            # Note: This may not work for all blob URLs
            logger.info("      Attempting to resolve blob URL...")

            # Try to find Google Storage URL in page content
            body_html = self.driver.page_source

            import re
            # Pattern for Google Storage URLs
            gcs_pattern = r'https://storage\.googleapis\.com/[^\s"\'<>]+'
            matches = re.findall(gcs_pattern, body_html)

            if matches:
                # Filter for video files
                video_matches = [m for m in matches if any(ext in m.lower() for ext in ['.mp4', '.webm', 'video'])]
                if video_matches:
                    logger.info(f"      Found Google Storage URL: {video_matches[0][:80]}...")
                    return video_matches[0]

            return None

        except Exception as e:
            logger.debug(f"      Could not convert blob URL: {e}")
            return None

    def _download_blob_video(self, blob_url: str) -> Optional[str]:
        """
        Download video from blob URL and save locally
        Returns local file path
        """
        try:
            from datetime import datetime
            logger.info("      Downloading video from blob URL...")

            # Use JavaScript to convert blob to base64
            video_base64 = self.driver.execute_async_script("""
                let blobUrl = arguments[0];
                let callback = arguments[1];

                fetch(blobUrl)
                    .then(r => r.blob())
                    .then(blob => {
                        let reader = new FileReader();
                        reader.onload = () => callback(reader.result);
                        reader.readAsDataURL(blob);
                    })
                    .catch(err => {
                        console.error('Blob fetch error:', err);
                        callback(null);
                    });
            """, blob_url)

            if video_base64:
                # Decode base64 and save
                import base64
                video_data = base64.b64decode(video_base64.split(',')[1])

                # Save to data/videos directory
                os.makedirs(self.download_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_{timestamp}.mp4"
                filepath = os.path.join(self.download_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(video_data)

                logger.info(f"      ✅ Video downloaded: {filepath}")
                return filepath
            else:
                logger.error("      ❌ Failed to fetch blob data")
                return None

        except Exception as e:
            logger.error(f"      Error downloading blob video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def close(self):
        """Close the browser"""
        if self.driver:
            logger.info("👋 Closing Comet browser...")
            self.driver.quit()
            logger.info("✅ Browser closed")

    def save_screenshot(self, filename: str = None):
        """Save screenshot for debugging"""
        if not filename:
            from datetime import datetime
            filename = f"./comet_screenshot_{datetime.now().strftime('%H%M%S')}.png"

        self.driver.save_screenshot(filename)
        logger.info(f"📸 Screenshot saved: {filename}")

    def save_page_html(self, filename: str = None):
        """Save page HTML for debugging"""
        if not filename:
            from datetime import datetime
            filename = f"./comet_page_{datetime.now().strftime('%H%M%S')}.html"

        with open(filename, 'w') as f:
            f.write(self.driver.page_source)

        logger.info(f"💾 HTML saved: {filename}")
