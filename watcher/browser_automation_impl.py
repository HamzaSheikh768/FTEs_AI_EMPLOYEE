#!/usr/bin/env python3
"""
Browser Automation Implementation for Personal AI Employee
Handles web browser automation for forms, payments, and general interactions
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from typing import List, Dict, Any, Optional


class BrowserAutomation:
    def __init__(self, vault_path="AI_Employee_Vault"):
        """
        Initialize Browser Automation

        Args:
            vault_path (str): Path to the AI Employee vault
        """
        self.vault_path = Path(vault_path)
        self.browser = None
        self.page = None

    def setup_browser(self, headless=True, browser_type="chromium"):
        """Setup Playwright browser instance"""
        try:
            playwright = sync_playwright().start()

            # Select browser type
            if browser_type == "chromium":
                browser_class = playwright.chromium
            elif browser_type == "firefox":
                browser_class = playwright.firefox
            elif browser_type == "webkit":
                browser_class = playwright.webkit
            else:
                browser_class = playwright.chromium

            # Launch browser
            self.browser = browser_class.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--disable-gpu'
                ]
            )

            # Create new page
            self.page = self.browser.new_page()

            # Set up basic browser context
            self.page.set_default_timeout(30000)  # 30 second timeout

            # Set viewport size
            self.page.set_viewport_size({"width": 1280, "height": 800})

            print(f"Browser setup successful (type: {browser_type}, headless: {headless})")
            return True

        except Exception as e:
            print(f"Error setting up browser: {e}")
            return False

    def navigate_and_act(self, url: str, actions: List[Dict[str, Any]]) -> bool:
        """Navigate to URL and perform actions"""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call setup_browser() first.")

        try:
            # Check for dry run mode
            if os.getenv("BROWSER_DRY_RUN", "false").lower() == "true":
                print(f"[DRY RUN] Would navigate to {url} and perform {len(actions)} actions")
                for i, action in enumerate(actions):
                    print(f"  Action {i+1}: {action}")
                return True

            # Navigate to URL
            print(f"Navigating to: {url}")
            self.page.goto(url, wait_until="networkidle")

            # Perform each action
            for i, action in enumerate(actions):
                print(f"Performing action {i+1}/{len(actions)}: {action.get('type', 'unknown')}")
                success = self._perform_action(action)
                if not success:
                    print(f"Action {i+1} failed: {action}")
                    return False

                # Wait between actions
                time.sleep(1)

            return True

        except PlaywrightTimeoutError:
            print(f"Timeout while navigating to {url}")
            return False
        except Exception as e:
            print(f"Error in navigate_and_act: {e}")
            return False

    def _perform_action(self, action: Dict[str, Any]) -> bool:
        """Perform a single browser action"""
        action_type = action.get("type", "").lower()

        try:
            if action_type == "click":
                return self._click_element(action)
            elif action_type == "fill":
                return self._fill_input(action)
            elif action_type == "select":
                return self._select_option(action)
            elif action_type == "upload":
                return self._upload_file(action)
            elif action_type == "wait":
                return self._wait_for_element(action)
            elif action_type == "scroll":
                return self._scroll_page(action)
            elif action_type == "screenshot":
                return self._take_screenshot(action)
            elif action_type == "extract":
                return self._extract_text(action)
            elif action_type == "javascript":
                return self._execute_javascript(action)
            else:
                print(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            print(f"Error performing action {action_type}: {e}")
            return False

    def _click_element(self, action: Dict[str, Any]) -> bool:
        """Click an element"""
        selector = action.get("selector")
        if not selector:
            print("No selector provided for click action")
            return False

        try:
            element = self.page.wait_for_selector(selector, timeout=10000)
            element.click()
            return True
        except PlaywrightTimeoutError:
            print(f"Element not found: {selector}")
            return False

    def _fill_input(self, action: Dict[str, Any]) -> bool:
        """Fill an input field"""
        selector = action.get("selector")
        value = action.get("value", "")

        if not selector:
            print("No selector provided for fill action")
            return False

        try:
            element = self.page.wait_for_selector(selector, timeout=10000)
            element.fill(value)
            return True
        except PlaywrightTimeoutError:
            print(f"Input not found: {selector}")
            return False

    def _select_option(self, action: Dict[str, Any]) -> bool:
        """Select an option from a dropdown"""
        selector = action.get("selector")
        value = action.get("value", "")

        if not selector:
            print("No selector provided for select action")
            return False

        try:
            element = self.page.wait_for_selector(selector, timeout=10000)
            element.select_option(value)
            return True
        except PlaywrightTimeoutError:
            print(f"Select element not found: {selector}")
            return False

    def _upload_file(self, action: Dict[str, Any]) -> bool:
        """Upload a file"""
        selector = action.get("selector")
        file_path = action.get("file_path")

        if not selector or not file_path:
            print("Selector and file_path required for upload action")
            return False

        try:
            element = self.page.wait_for_selector(selector, timeout=10000)
            element.set_input_files(file_path)
            return True
        except PlaywrightTimeoutError:
            print(f"File input not found: {selector}")
            return False
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def _wait_for_element(self, action: Dict[str, Any]) -> bool:
        """Wait for an element to appear"""
        selector = action.get("selector")
        timeout = action.get("timeout", 10000)

        if not selector:
            print("No selector provided for wait action")
            return False

        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            print(f"Element did not appear: {selector}")
            return False

    def _scroll_page(self, action: Dict[str, Any]) -> bool:
        """Scroll the page"""
        direction = action.get("direction", "down")
        amount = action.get("amount", 500)

        try:
            if direction == "down":
                self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "top":
                self.page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            time.sleep(0.5)  # Wait for scroll to complete
            return True
        except Exception as e:
            print(f"Error scrolling: {e}")
            return False

    def _take_screenshot(self, action: Dict[str, Any]) -> bool:
        """Take a screenshot"""
        file_path = action.get("file_path", f"screenshot_{int(time.time())}.png")

        try:
            self.page.screenshot(path=file_path, full_page=True)
            print(f"Screenshot saved: {file_path}")
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False

    def _extract_text(self, action: Dict[str, Any]) -> bool:
        """Extract text from an element"""
        selector = action.get("selector")
        save_to = action.get("save_to")

        if not selector:
            print("No selector provided for extract action")
            return False

        try:
            element = self.page.wait_for_selector(selector, timeout=10000)
            text = element.inner_text()

            if save_to:
                # Save extracted text to file
                with open(save_to, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Text extracted and saved to: {save_to}")
            else:
                print(f"Extracted text: {text[:100]}...")

            return True
        except PlaywrightTimeoutError:
            print(f"Element not found for extraction: {selector}")
            return False

    def _execute_javascript(self, action: Dict[str, Any]) -> bool:
        """Execute JavaScript code"""
        script = action.get("script")
        if not script:
            print("No script provided for javascript action")
            return False

        try:
            result = self.page.evaluate(script)
            if result is not None:
                print(f"Script result: {result}")
            return True
        except Exception as e:
            print(f"Error executing JavaScript: {e}")
            return False

    def take_screenshot(self, file_path: Optional[str] = None) -> bool:
        """Take a screenshot of the current page"""
        if not self.page:
            print("Browser not initialized")
            return False

        if not file_path:
            timestamp = int(time.time())
            file_path = f"screenshot_{timestamp}.png"

        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Take screenshot
            self.page.screenshot(path=file_path, full_page=True)
            print(f"Screenshot saved: {file_path}")
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False

    def get_page_title(self) -> str:
        """Get the current page title"""
        if not self.page:
            return ""
        return self.page.title()

    def get_current_url(self) -> str:
        """Get the current URL"""
        if not self.page:
            return ""
        return self.page.url

    def wait_for_navigation(self, timeout: int = 30000) -> bool:
        """Wait for page navigation to complete"""
        if not self.page:
            return False

        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            print("Navigation timeout")
            return False

    def close(self):
        """Close the browser instance"""
        if self.browser:
            self.browser.close()
            print("Browser closed")


def main():
    """Main function for testing browser automation"""
    import argparse

    parser = argparse.ArgumentParser(description="Browser Automation for Personal AI Employee")
    parser.add_argument("--url", help="URL to navigate to")
    parser.add_argument("--actions", help="JSON file with actions to perform")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")
    parser.add_argument("--screenshot", help="Take screenshot and save to path")

    args = parser.parse_args()

    automation = BrowserAutomation()

    try:
        # Setup browser
        if not automation.setup_browser(headless=args.headless):
            print("Failed to setup browser")
            return

        # Set dry run mode
        if args.dry_run:
            os.environ["BROWSER_DRY_RUN"] = "true"

        if args.url and args.actions:
            # Load actions from file
            with open(args.actions, 'r') as f:
                actions = json.load(f)

            # Navigate and perform actions
            success = automation.navigate_and_act(args.url, actions)
            if success:
                print("All actions completed successfully")
            else:
                print("Some actions failed")

        elif args.url:
            # Just navigate to URL
            automation.page.goto(args.url)
            print(f"Navigated to: {args.url}")
            print(f"Page title: {automation.get_page_title()}")

        else:
            print("No URL specified. Use --url to navigate to a page")

        # Take screenshot if requested
        if args.screenshot:
            automation.take_screenshot(args.screenshot)

    finally:
        automation.close()


if __name__ == "__main__":
    main()