"""
Test script to verify Playwright setup for LinkedIn automation
"""
from playwright.sync_api import sync_playwright
import time

def test_playwright_setup():
    """Test basic Playwright functionality"""
    print("Testing Playwright setup...")

    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)  # Use headless for testing
            page = browser.new_page()

            # Test navigation to LinkedIn
            print("Navigating to LinkedIn login page...")
            page.goto("https://www.linkedin.com/login")

            # Check if we can interact with the page
            title = page.title()
            print(f"Page title: {title}")

            # Try to find login elements
            try:
                username_field = page.wait_for_selector("input#username", timeout=5000)
                password_field = page.wait_for_selector("input#password", timeout=5000)
                login_button = page.wait_for_selector("button[type='submit']", timeout=5000)

                print("✓ Found LinkedIn login elements")
                print("✓ Playwright setup is working correctly")

                # Close browser
                browser.close()
                return True
            except Exception as e:
                print(f"✗ Error finding login elements: {e}")
                browser.close()
                return False

    except Exception as e:
        print(f"✗ Error with Playwright: {e}")
        return False

if __name__ == "__main__":
    success = test_playwright_setup()
    if success:
        print("\n✓ Playwright successfully set up for LinkedIn automation!")
    else:
        print("\n✗ Playwright setup failed.")