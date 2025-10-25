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
        """
        Create a new project by navigating to new UUID URL
        Flow auto-creates project when you navigate to /project/{UUID}

        Args:
            title: Project title (not used, just for reference)

        Returns:
            Project ID (UUID) if successful, None otherwise
        """
        try:
            import uuid

            # Generate UUID v4
            project_id = str(uuid.uuid4()).upper()

            # Navigate to new project URL (Flow auto-creates project)
            project_url = f"https://labs.google/fx/vi/tools/flow/project/{project_id}"
            logger.info(f"   📁 Creating project with ID: {project_id}")
            logger.info(f"   🌐 Navigating to: {project_url}")

            self.driver.get(project_url)

            # Wait for Flow to initialize the project
            time.sleep(5)

            # Verify we're on the project page
            if "project" in self.driver.current_url and project_id in self.driver.current_url:
                logger.info(f"   ✅ Project created successfully: {project_id}")
                return project_id
            else:
                logger.error(f"   ❌ Failed to create project. Current URL: {self.driver.current_url}")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error creating project: {str(e)}")
            import traceback
            traceback.print_exc()
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
        logger.info(f"   Prompt ({len(prompt)} chars): {prompt[:100]}...")
        logger.info(f"   Full prompt: {prompt}")

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

            # Step 2: Fill prompt (with better interaction)
            logger.info("   📝 Filling prompt...")

            # Scroll to textarea
            self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            time.sleep(0.5)

            # Click to focus
            textarea.click()
            time.sleep(0.5)

            # Clear using JavaScript (more reliable)
            self.driver.execute_script("arguments[0].value = '';", textarea)

            # Fill using send_keys (triggers proper events)
            textarea.send_keys(prompt)

            # Wait for Flow to process the input
            time.sleep(3)
            logger.info("   ✅ Prompt filled")

            # Step 3: Find and click Generate button
            logger.info("   🎬 Looking for Generate button...")
            generate_button = self._find_generate_button()
            if not generate_button:
                logger.error("   ❌ Generate button not found")
                return None

            # Wait until button is fully enabled
            max_wait = 10
            for i in range(max_wait):
                if generate_button.is_enabled():
                    break
                logger.info(f"   ⏳ Waiting for button to enable... ({i+1}/{max_wait}s)")
                time.sleep(1)
                # Re-find button in case DOM changed
                generate_button = self._find_generate_button()
                if not generate_button:
                    logger.error("   ❌ Generate button disappeared")
                    return None

            # Step 3.5: Get current video URLs before generating (to track new one)
            import re
            page_before = self.driver.page_source
            gcs_pattern = r'https://storage\.googleapis\.com/ai-sandbox-videofx/video/[a-f0-9\-]+'
            urls_before = set(re.findall(gcs_pattern, page_before))
            logger.info(f"   📊 Current videos on page: {len(urls_before)}")

            logger.info("   🎬 Clicking Generate button...")
            # Use JavaScript click for more reliability
            self.driver.execute_script("arguments[0].click();", generate_button)
            time.sleep(3)
            logger.info("   ✅ Generate button clicked")

            # Step 4: Wait for video generation to complete
            logger.info("   ⏳ Waiting for video generation...")
            success = self._wait_for_video_generation(progress_callback=progress_callback, urls_before=urls_before)

            if success:
                logger.info("   ✅ Video generation completed!")

                # Extract video URL from page (pass urls_before to find new URL)
                video_url = self._extract_video_url(urls_before=urls_before)

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

    def _wait_for_video_generation(self, timeout: int = 120, progress_callback=None, urls_before=None) -> bool:
        """
        Wait for video generation to complete with real-time progress tracking

        Args:
            timeout: Maximum wait time in seconds
            progress_callback: Optional callback function(elapsed, percent)

        Returns:
            True if video generated successfully, False otherwise
        """
        logger.info(f"      Waiting up to {timeout}s for generation...")

        start_time = time.time()
        check_interval = 3  # Check every 3 seconds for more frequent updates

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            percent = int((elapsed / timeout) * 100)

            logger.info(f"      ⏳ Progress: {percent}% ({elapsed}s / {timeout}s)")

            # Call progress callback if provided
            if progress_callback:
                try:
                    progress_callback(elapsed, percent)
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

    def _extract_video_url(self, urls_before=None) -> Optional[str]:
        """
        Extract video URL from Flow page after video generation completes
        Strategy: Find the NEWEST Google Storage URL by comparing before/after
        """
        try:
            # Method 1: Extract Google Storage URL from page source (most reliable)
            logger.info("      Searching for Google Storage URL in page source...")

            import re
            page_source = self.driver.page_source

            # Pattern for Google Storage video URLs
            gcs_pattern = r'https://storage\.googleapis\.com/ai-sandbox-videofx/video/[a-f0-9\-]+'
            urls_after = set(re.findall(gcs_pattern, page_source))

            logger.info(f"      Found {len(urls_after)} Google Storage URLs on page")

            if urls_before is not None:
                # Find NEW URLs (appeared after video generation)
                new_urls = urls_after - urls_before
                if new_urls:
                    # Flow is set to create 1 video per prompt
                    # Get the first (and should be only) new URL
                    new_urls_sorted = sorted(list(new_urls))
                    latest_url = new_urls_sorted[0]
                    logger.info(f"      ✅ Found {len(new_urls)} NEW video URL(s)")
                    logger.info(f"      {latest_url[:80]}...")
                    return latest_url
                else:
                    logger.warning("      ⚠️  No new URLs found, using last URL")
                    if urls_after:
                        latest_url = sorted(list(urls_after))[-1]
                        logger.info(f"      Using last URL: {latest_url[:80]}...")
                        return latest_url
            else:
                # No before URLs provided, use last URL
                if urls_after:
                    latest_url = sorted(list(urls_after))[-1]
                    logger.info(f"      ✅ Found Google Storage URL: {latest_url[:80]}...")
                    return latest_url

            # Method 2: Fallback to blob URL download
            logger.warning("      No Google Storage URL found, trying blob URL...")
            video_elements = self.driver.find_elements(By.TAG_NAME, 'video')

            if not video_elements:
                logger.warning("      No video elements found")
                return None

            # Get the last visible video
            latest_video = None
            for video in reversed(video_elements):
                if video.is_displayed():
                    latest_video = video
                    break

            if not latest_video:
                logger.warning("      No visible video found")
                return None

            src = latest_video.get_attribute('src')
            if not src:
                logger.warning("      Video has no src attribute")
                return None

            logger.info(f"      Found blob src: {src[:80]}...")

            # Download blob video
            if src.startswith('blob:'):
                logger.info("      Downloading blob video to local file...")
                local_path = self._download_blob_video(src)
                if local_path:
                    logger.info(f"      ✅ Video saved locally: {local_path}")
                    return local_path
                else:
                    logger.error("      ❌ Failed to download blob video")
                    return None
            else:
                return src

        except Exception as e:
            logger.error(f"      Error extracting video URL: {e}")
            import traceback
            traceback.print_exc()
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

    def save_page_html(self, filename: str = None):
        """Save page HTML for debugging"""
        if not filename:
            from datetime import datetime
            filename = f"./comet_page_{datetime.now().strftime('%H%M%S')}.html"

        with open(filename, 'w') as f:
            f.write(self.driver.page_source)

        logger.info(f"💾 HTML saved: {filename}")
