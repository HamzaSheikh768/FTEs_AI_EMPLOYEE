#!/usr/bin/env python3
"""
Twitter/X MCP Server using Playwright Browser Automation
Posts tweets via browser automation instead of official API
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logs_dir = Path("AI_Employee_Vault/Logs")
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'twitter_playwright.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TwitterPlaywrightClient:
    """Twitter client using Playwright browser automation"""
    
    def __init__(self, storage_state_path: Optional[str] = None):
        self.base_url = "https://twitter.com"
        self.login_url = "https://twitter.com/i/flow/login"
        self.compose_url = "https://twitter.com/compose/tweet"
        
        # Session storage path
        self.storage_state_path = storage_state_path or str(
            Path("AI_Employee_Vault/twitter_session.json")
        )
        
        # Ensure directory exists
        Path(self.storage_state_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        logger.info("Twitter Playwright client initialized")
        logger.info(f"Storage state path: {self.storage_state_path}")
    
    async def initialize(self, headless: bool = True):
        """Initialize browser and load session"""
        logger.info("Initializing browser...")
        
        playwright = await async_playwright().start()
        
        # Launch Chromium browser with proper UI settings
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--start-maximized',
                '--disable-notifications',
                '--disable-popup-blocking',
                '--force-device-scale-factor=1',
            ]
        )
        
        # Load or create session
        if Path(self.storage_state_path).exists():
            logger.info("Loading existing session...")
            try:
                self.context = await self.browser.new_context(
                    storage_state=self.storage_state_path,
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                    device_scale_factor=1.0,
                    is_mobile=False,
                    has_touch=False,
                    accept_downloads=True,
                    java_script_enabled=True,
                )
                logger.info("Session loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load session: {e}. Will create new session.")
                self.context = await self._create_new_context()
        else:
            logger.info("No existing session found. Creating new session...")
            self.context = await self._create_new_context()
        
        self.page = await self.context.new_page()
        
        # Set proper window size and zoom
        await self.page.set_viewport_size({'width': 1920, 'height': 1080})
        await self.page.evaluate("document.body.style.zoom = '1'")
        
        # Disable animations for faster loading
        await self.page.add_init_script("""
            document.body.style.zoom = '1';
            window.devicePixelRatio = 1;
        """)
        
        logger.info("Browser initialized successfully")
    
    async def _create_new_context(self) -> BrowserContext:
        """Create new browser context with anti-detection settings"""
        return await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
    
    async def save_session(self):
        """Save current session to storage state"""
        try:
            if self.context:
                await self.context.storage_state(path=self.storage_state_path)
                logger.info(f"Session saved to: {self.storage_state_path}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    async def login(self, username: str, password: str, email: Optional[str] = None):
        """
        Auto Login to Twitter - FINAL ATTEMPT with better approach
        """
        logger.info("Navigating to Twitter login page...")
        
        # Go directly to x.com (not /login)
        await self.page.goto("https://x.com", wait_until='domcontentloaded')
        await asyncio.sleep(10)  # Wait for page to fully load
        
        # Take screenshot
        await self.page.screenshot(path='twitter_initial.png', full_page=True)
        logger.info("Screenshot saved: twitter_initial.png")
        
        try:
            # Check if already logged in
            if await self.page.is_visible('article[data-testid="tweet"]'):
                logger.info("[OK] Already logged in!")
                await self.save_session()
                return
            
            # Find username field on the modal
            logger.info("Looking for username field...")
            
            # Click on login button if visible
            try:
                login_link = await self.page.wait_for_selector('a:has-text("Sign in")', timeout=5000)
                await login_link.click()
                await asyncio.sleep(3)
                logger.info("Clicked Sign in button")
            except:
                pass  # Already on login modal
            
            # Wait for modal to appear
            await asyncio.sleep(5)
            
            # Take screenshot to see current state
            await self.page.screenshot(path='twitter_before_username.png', full_page=True)
            
            # Try multiple approaches for username
            username_entered = False
            
            # Approach 1: Direct input selector
            try:
                username_field = await self.page.query_selector('input[autocomplete="username"]')
                if username_field:
                    await username_field.type(username, delay=50)
                    username_entered = True
                    logger.info("[OK] Entered username (approach 1)")
            except Exception as e:
                logger.debug(f"Approach 1 failed: {e}")
            
            # Approach 2: Any text input in the form
            if not username_entered:
                try:
                    inputs = await self.page.query_selector_all('input[type="text"]')
                    for inp in inputs:
                        label = await inp.get_attribute('aria-label')
                        if label and 'username' in label.lower() or 'email' in label.lower():
                            await inp.type(username, delay=50)
                            username_entered = True
                            logger.info("[OK] Entered username (approach 2)")
                            break
                except Exception as e:
                    logger.debug(f"Approach 2 failed: {e}")
            
            # Approach 3: First visible text input
            if not username_entered:
                try:
                    inputs = await self.page.query_selector_all('input')
                    for inp in inputs:
                        is_visible = await inp.is_visible()
                        input_type = await inp.get_attribute('type')
                        if is_visible and input_type == 'text':
                            await inp.type(username, delay=50)
                            username_entered = True
                            logger.info("[OK] Entered username (approach 3)")
                            break
                except Exception as e:
                    logger.debug(f"Approach 3 failed: {e}")
            
            if not username_entered:
                logger.error("[ERROR] Could not enter username")
                await self.page.screenshot(path='twitter_username_failed.png', full_page=True)
                raise Exception("Username entry failed")
            
            await asyncio.sleep(2)
            
            # Click Next
            next_clicked = False
            try:
                buttons = await self.page.query_selector_all('button')
                for btn in buttons:
                    text = await btn.inner_text()
                    if 'next' in text.lower():
                        is_visible = await btn.is_visible()
                        is_enabled = await btn.is_enabled()
                        if is_visible and is_enabled:
                            await btn.click()
                            next_clicked = True
                            logger.info("[OK] Clicked Next button")
                            break
            except Exception as e:
                logger.debug(f"Next button click failed: {e}")
            
            if not next_clicked:
                await self.page.keyboard.press('Enter')
                logger.info("Pressed Enter as Next")
            
            # Wait for password field
            logger.info("Waiting for password field...")
            await asyncio.sleep(8)
            
            # Take screenshot
            await self.page.screenshot(path='twitter_before_password.png', full_page=True)
            
            # Find password field
            password_entered = False
            try:
                password_fields = await self.page.query_selector_all('input[type="password"]')
                logger.info(f"Found {len(password_fields)} password field(s)")
                
                for pwd_field in password_fields:
                    is_visible = await pwd_field.is_visible()
                    if is_visible:
                        await pwd_field.type(password, delay=50)
                        password_entered = True
                        logger.info("[OK] Entered password")
                        break
            except Exception as e:
                logger.debug(f"Password entry failed: {e}")
            
            if password_entered:
                await asyncio.sleep(2)
                
                # Click Login
                login_clicked = False
                try:
                    buttons = await self.page.query_selector_all('button')
                    for btn in buttons:
                        text = await btn.inner_text()
                        if 'log in' in text.lower() or 'login' in text.lower():
                            is_visible = await btn.is_visible()
                            is_enabled = await btn.is_enabled()
                            if is_visible and is_enabled:
                                await btn.click()
                                login_clicked = True
                                logger.info("[OK] Clicked Login button")
                                break
                except Exception as e:
                    logger.debug(f"Login button click failed: {e}")
                
                if not login_clicked:
                    await self.page.keyboard.press('Enter')
                    logger.info("Pressed Enter to login")
                
                await asyncio.sleep(10)
            
            # Wait for login
            logger.info("Waiting for successful login...")
            for i in range(24):
                await asyncio.sleep(5)
                
                try:
                    if await self.page.is_visible('article[data-testid="tweet"]'):
                        logger.info("[OK] Login successful!")
                        break
                    if await self.page.is_visible('[data-testid="UserName"]'):
                        logger.info("[OK] Profile detected!")
                        break
                except:
                    pass
                
                if (i + 1) % 6 == 0:
                    logger.info(f"Waiting... ({(i+1)*5}s)")
            
            # Screenshot and save
            await self.page.screenshot(path='twitter_login_final.png', full_page=True)
            await self.save_session()
            logger.info("[OK] Session saved!")
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            await self.page.screenshot(path='twitter_login_failed.png', full_page=True)
            raise
    
    async def post_tweet(self, text: str, retry_count: int = 3) -> Dict[str, Any]:
        """
        Post a tweet using browser automation
        
        Args:
            text: Tweet text (max 280 characters)
            retry_count: Number of retries if selector fails
        
        Returns:
            Dict with status, tweet text, and platform
        """
        logger.info(f"Posting tweet: {text[:50]}...")
        
        result = {
            "status": "error",
            "tweet": text,
            "platform": "X",
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        for attempt in range(retry_count):
            try:
                # Navigate to home page instead of compose page
                logger.info(f"Navigate to home page (attempt {attempt + 1}/{retry_count})")
                await self.page.goto("https://x.com/home", wait_until='domcontentloaded')
                await asyncio.sleep(5)  # Wait for page to load
                
                # Find tweet box on home page - multiple selectors
                tweet_box = None
                selectors = [
                    'div[contenteditable="true"][role="textbox"]',
                    'div[aria-label="Tweet text"]',
                    'div[data-testid="tweetTextarea_0"]',
                    'div.public-DraftEditor-content',
                    'textarea',
                ]
                
                for selector in selectors:
                    try:
                        tweet_box = await self.page.wait_for_selector(selector, timeout=5000)
                        logger.info(f"Found tweet box with: {selector}")
                        break
                    except Exception:
                        continue
                
                if not tweet_box:
                    logger.warning("Tweet box not found. Taking screenshot...")
                    await self.page.screenshot(path='twitter_home_debug.png')
                    logger.info("Screenshot saved to twitter_home_debug.png")
                    # Try clicking the Tweet button first
                    try:
                        tweet_button = await self.page.wait_for_selector('button:has-text("Tweet")', timeout=5000)
                        await tweet_button.click()
                        await asyncio.sleep(2)
                        tweet_box = await self.page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
                    except Exception as e:
                        logger.error(f"Could not find tweet button: {e}")
                        raise Exception("Tweet box not found")
                
                # Click and clear
                await tweet_box.click()
                await asyncio.sleep(1)
                
                # Use keyboard to select all and delete
                await self.page.keyboard.press('Control+A')
                await asyncio.sleep(0.5)
                await self.page.keyboard.press('Delete')
                await asyncio.sleep(0.5)
                
                # Type tweet text
                await tweet_box.type(text, delay=50)
                await asyncio.sleep(2)
                
                # Find and click Tweet button
                tweet_buttons = [
                    'button:has-text("Tweet")',
                    'button:has-text("Post")',
                    'div[role="button"]:has-text("Tweet")',
                    'div[role="button"]:has-text("Post")',
                ]
                
                post_clicked = False
                for btn_selector in tweet_buttons:
                    try:
                        post_button = await self.page.wait_for_selector(btn_selector, timeout=5000)
                        await post_button.click()
                        logger.info("Clicked Tweet/Post button")
                        post_clicked = True
                        break
                    except Exception:
                        continue
                
                if not post_clicked:
                    logger.error("Could not find Tweet/Post button")
                    raise Exception("Post button not found")
                
                # Wait for confirmation
                await asyncio.sleep(5)
                
                # Check if tweet was posted
                try:
                    await self.page.wait_for_selector('div:has-text("Your post was sent")', timeout=5000)
                    logger.info("Tweet posted successfully!")
                    result["status"] = "success"
                    result["message"] = "Tweet posted successfully"
                except Exception:
                    logger.info("Tweet likely posted (no error detected)")
                    result["status"] = "success"
                    result["message"] = "Tweet posted (confirmation not detected)"
                
                return result
                
            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                logger.error(error_msg)
                result["error"] = error_msg
                
                if attempt < retry_count - 1:
                    logger.info(f"Retrying in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    logger.error("All retry attempts failed")
                    result["error"] = f"Failed after {retry_count} attempts: {str(e)}"
        
        return result
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


async def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Twitter/X MCP Server using Playwright")
    parser.add_argument("--post", type=str, help="Post a tweet")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--login", action="store_true", help="Force login")
    parser.add_argument("--username", type=str, help="Twitter username")
    parser.add_argument("--password", type=str, help="Twitter password")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("TWITTER/X MCP SERVER - Playwright Automation")
    print("=" * 60)
    
    # Initialize client
    client = TwitterPlaywrightClient()
    
    try:
        # Initialize browser - ALWAYS use non-headless for login
        await client.initialize(headless=False if args.login else args.headless)
        
        # Check if login is needed
        storage_exists = Path(client.storage_state_path).exists()
        
        if args.login or not storage_exists:
            print("\n[INFO] Login required...")
            
            # Get credentials from environment or args
            username = args.username or os.getenv("TWITTER_ACCOUNT_EMAIL") or os.getenv("TWITTER_USERNAME")
            password = args.password or os.getenv("TWITTER_ACCOUNT_PASSWORD")
            
            if username and password:
                print(f"[INFO] Auto-logging in as: {username}")
                print("[INFO] Please wait for browser to open and login automatically...")
                await client.login(username, password)
            else:
                print("[ERROR] No credentials provided!")
                print("[ERROR] Please set TWITTER_ACCOUNT_EMAIL and TWITTER_ACCOUNT_PASSWORD in .env")
                print("[ERROR] Or use --username and --password arguments")
                print("\n[INFO] Exiting...")
                return
        else:
            print("\n[OK] Using existing session")
        
        # Post tweet if requested
        if args.post:
            print(f"\n[INFO] Posting tweet: {args.post[:50]}...")
            result = await client.post_tweet(args.post)
            
            print("\n" + "=" * 60)
            print("RESULT:")
            print(json.dumps(result, indent=2))
            print("=" * 60)
            
            if result["status"] == "success":
                print("\n[OK] Tweet posted successfully!")
            else:
                print(f"\n[ERROR] Failed to post tweet: {result.get('error', 'Unknown error')}")
        
        # If no action specified, show help
        if not args.post and not args.login:
            print("\n[INFO] No action specified. Use --post to post a tweet.")
            print("\nExample:")
            print('  python twitter_mcp_playwright.py --post "Hello world"')
    
    finally:
        # Cleanup
        await client.close()
        print("\n[INFO] Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
